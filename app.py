from flask import Flask, render_template, request, jsonify
from PyPDF2 import PdfReader
import google.generativeai as genai
import os
import json

# Configure Google API Key
os.environ["GOOGLE_API_KEY"] = "ADD YOUR API"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize Flask app
app = Flask(__name__)

# Load Google Gemini Model
model = genai.GenerativeModel("models/gemini-1.5-pro")


def extract_resume_details(resume_text):
    """Parses resume text using Google Gemini and returns structured JSON."""
    prompt = f"""
    You are an advanced AI assistant that extracts structured data from resumes.
    Given the resume text below, return the details in a clean JSON format:

    Resume Text:
    {resume_text}

    Extract:
    - Full Name
    - Contact Number
    - Email Address
    - Location
    - Skills (split into Technical and Non-Technical)
    - Education (Degree, Institution, Year)
    - Work Experience (Job Title, Company, Years, Responsibilities)
    - Certifications
    - Languages spoken
    - Suggested Resume Category
    - Recommended Job Roles

    Ensure the response is in valid JSON format.
    """

    # Generate structured response from the AI model
    response = model.generate_content(prompt).text

    # Clean the response to remove markdown formatting
    cleaned_response = response.replace("```json", "").replace("```", "").strip()

    # Convert the response into a Python dictionary
    return json.loads(cleaned_response)


@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')


@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Handles resume upload, extracts data, and returns a parsed response."""
    if 'resume' not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"})

    if file and file.filename.endswith('.pdf'):
        # Extract text from PDF
        reader = PdfReader(file)
        resume_text = "".join([page.extract_text() for page in reader.pages])

        # Parse resume details using AI
        resume_data = extract_resume_details(resume_text)

        # Extract individual fields for rendering
        full_name = resume_data.get("Full Name", "N/A")
        contact_number = resume_data.get("Contact Number", "N/A")
        email_address = resume_data.get("Email Address", "N/A")
        location = resume_data.get("Location", "N/A")

        # Skills
        skills = resume_data.get("Skills", {})
        technical_skills = ", ".join(skills.get("Technical Skills", []))
        non_technical_skills = ", ".join(skills.get("Non-Technical Skills", []))

        # Education
        education_list = resume_data.get("Education", [])
        education_str = "\n".join([
            f"{edu.get('Degree', 'N/A')} from {edu.get('Institution', 'N/A')} (Graduated: {edu.get('Years', 'N/A')})"
            for edu in education_list
        ])

        # Work Experience
        work_experience_list = resume_data.get("Work Experience", [])
        work_experience_str = "\n".join([
            f"{job.get('Job Title', 'N/A')} at {job.get('Company Name', 'N/A')} ({job.get('Years of Experience', 'N/A')})\nResponsibilities: {', '.join(job.get('Responsibilities', [])).strip()}"
            for job in work_experience_list
        ])

        # Certifications
        certifications = ", ".join(resume_data.get("Certifications", []))

        # Languages
        languages = ", ".join(resume_data.get("Languages spoken", []))

        # Suggested Category & Job Roles
        suggested_resume_category = resume_data.get("Suggested Resume Category", "N/A")
        recommended_job_roles = ", ".join(resume_data.get("Recommended Job Roles", []))

        # Render extracted data in the updated AI-themed UI
        return render_template('index.html',
                               full_name=full_name,
                               contact_number=contact_number,
                               email_address=email_address,
                               location=location,
                               technical_skills=technical_skills,
                               non_technical_skills=non_technical_skills,
                               education=education_str,
                               work_experience=work_experience_str,
                               certifications=certifications,
                               languages=languages,
                               suggested_resume_category=suggested_resume_category,
                               recommended_job_roles=recommended_job_roles)


# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
