import pdfplumber
import spacy
import nltk
import re
import pandas as pd
import os
import logging
from PIL import Image
import pytesseract

# Download necessary resources
try:
    nltk.download('punkt')
    nlp = spacy.load('en_core_web_sm')
except Exception as e:
    logging.error(f"Error loading NLP resources: {str(e)}")
    # Fallback to basic functionality if resources cannot be loaded
    nlp = None

# Load skills dataset
try:
    skills_dataset_path = 'attached_assets/expanded_skills_with_web_app_and_database.csv'
    skills_df = pd.read_csv(skills_dataset_path)
    skills_list = [skill.lower() for skill in skills_df['skill'].tolist()]
except Exception as e:
    logging.error(f"Error loading skills dataset: {str(e)}")
    skills_list = []

# Define resume sections with variations for flexible extraction
resume_sections = {
    "Education": ["Education", "Academic Background", "Academic Qualifications", "Degree", "Educational Background"],
    "Projects": ["Projects", "Personal Projects", "Work Samples", "Project Experience", "Key Projects"],
    "Experience": ["Experience", "Work Experience", "Employment History", "Professional Experience", "Career History", "Work History"],
    "Skills": ["Skills", "Technical Skills", "Tools & Technologies", "Competencies", "Expertise", "Proficiency", "Tech Stack"],
    "Positions of Responsibility": ["Positions of Responsibility", "Leadership Roles", "Leadership Experience", "Leadership"],
    "Achievements": ["Achievements", "Awards & Honors", "Accomplishments", "Honors", "Recognitions"]
}

# Set model to None as we're using the fallback mechanism
model = None
logging.warning("Using fallback functionality for resume analysis")

def analyze_resume(file_path):
    """Analyze a resume file (PDF or image) and return the extracted text"""
    try:
        text = extract_text_from_file(file_path)
        return text
    except Exception as e:
        logging.error(f"Error analyzing resume: {str(e)}")
        return "Error extracting text from resume."

def extract_text_from_file(file_path):
    """Determine file type and extract text accordingly"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        return extract_text_from_image(file_path)
    else:
        logging.error(f"Unsupported file format: {ext}")
        raise ValueError(f"Unsupported file format: {ext}")

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    return text.strip()

def extract_text_from_image(image_path):
    """Extract text from an image using OCR"""
    try:
        image = Image.open(image_path)
        # Use pytesseract to extract text (OCR)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logging.error(f"Error during image OCR: {str(e)}")
        # If pytesseract not installed or error occurs
        return "Error: Could not extract text from image. Make sure pytesseract is installed correctly."

def preprocess_and_segment(text):
    """Preprocess the text and segment it into sections"""
    text = re.sub(r'\s+', ' ', text)
    sections_extracted = {key: "" for key in resume_sections.keys()}
    
    for section, variations in resume_sections.items():
        for variation in variations:
            escaped_sections = [re.escape(v) for v in sum(resume_sections.values(), [])]
            section_pattern = "|".join(escaped_sections)
            pattern = rf"(?i){re.escape(variation)}[ \t:.-]+(.*?)(?=\n\s*(?:{section_pattern})|$)"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections_extracted[section] = match.group(1).strip()
                break
    
    return sections_extracted

def extract_basic_info(text):
    """Extract basic information from resume text"""
    if not nlp:
        # Fallback to basic regex extraction if spacy isn't available
        return fallback_extract_basic_info(text)
    
    basic_info = {
        'name': '',
        'email': '',
        'phone': '',
        'skills': []
    }
    
    # Extract name (assuming it's at the top of the resume)
    lines = text.split('\n')
    if lines:
        # Assume the first non-empty line is the name
        for line in lines:
            if line.strip():
                basic_info['name'] = line.strip()
                break
    
    # Extract email using regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        basic_info['email'] = email_matches[0]
    
    # Extract phone number using regex
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?(?:\d{1,4}[-.\s]?)?\d{1,9}(?:[-.\s]?\d{1,5})?'
    phone_matches = re.findall(phone_pattern, text)
    if phone_matches:
        # Find the most likely phone number (usually 10+ digits when stripped of non-digits)
        candidates = [(p, len(re.sub(r'\D', '', p))) for p in phone_matches]
        candidates = [c for c in candidates if c[1] >= 10]  # Must have at least 10 digits
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)  # Sort by number of digits
            basic_info['phone'] = candidates[0][0]
    
    # Extract skills
    doc = nlp(text)
    extracted_skills = []
    
    # Check for skills from our predefined list
    for skill in skills_list:
        if skill.lower() in text.lower():
            # Verify it's a standalone word, not part of another word
            skill_pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(skill_pattern, text, re.IGNORECASE):
                extracted_skills.append(skill)
    
    basic_info['skills'] = list(set(extracted_skills))[:10]  # Limit to top 10 skills
    
    return basic_info

def fallback_extract_basic_info(text):
    """Fallback method for basic info extraction using regex only"""
    basic_info = {
        'name': '',
        'email': '',
        'phone': '',
        'skills': []
    }
    
    # Extract name (assuming it's at the top of the resume)
    lines = text.split('\n')
    if lines:
        # Assume the first non-empty line is the name
        for line in lines:
            if line.strip():
                basic_info['name'] = line.strip()
                break
    
    # Extract email using regex
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_matches = re.findall(email_pattern, text)
    if email_matches:
        basic_info['email'] = email_matches[0]
    
    # Extract phone number using regex
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?(?:\d{1,4}[-.\s]?)?\d{1,9}(?:[-.\s]?\d{1,5})?'
    phone_matches = re.findall(phone_pattern, text)
    if phone_matches:
        # Find the most likely phone number (usually 10+ digits when stripped of non-digits)
        candidates = [(p, len(re.sub(r'\D', '', p))) for p in phone_matches]
        candidates = [c for c in candidates if c[1] >= 10]  # Must have at least 10 digits
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)  # Sort by number of digits
            basic_info['phone'] = candidates[0][0]
    
    # Extract skills using basic matching
    skills_found = []
    for skill in skills_list:
        if skill.lower() in text.lower():
            # Verify it's a standalone word, not part of another word
            skill_pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(skill_pattern, text, re.IGNORECASE):
                skills_found.append(skill)
    
    basic_info['skills'] = list(set(skills_found))[:10]  # Limit to top 10 skills
    
    return basic_info

def extract_entities(text):
    """Extracts named entities from text using spaCy or regex fallback."""
    if not nlp:
        # Fallback to basic regex extraction
        return fallback_extract_entities(text)
    
    doc = nlp(text)
    entities = {
        "SKILLS": [],
        "COMPANIES": [],
        "EDUCATION": [],
        "TOOLS": []
    }
    
    # Extract entities based on spaCy's NER
    for ent in doc.ents:
        if ent.label_ == "ORG":
            entities["COMPANIES"].append(ent.text)
        
    # Extract skills using our predefined list
    for skill in skills_list:
        if skill and skill.lower() in text.lower():
            # Verify it's a standalone word
            skill_pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(skill_pattern, text, re.IGNORECASE):
                entities["SKILLS"].append(skill)
    
    # Extract education terms
    education_patterns = [
        r'\b(Bachelor|Master|MBA|PhD|BSc|MSc|BA|MA|MD|JD)\b',
        r'\b(University|College|School|Institute|Academy)\b',
        r'\b(Degree|Diploma|Certificate)\b'
    ]
    
    for pattern in education_patterns:
        matches = re.findall(pattern, text)
        entities["EDUCATION"].extend(matches)
    
    # Extract tools and technologies
    tool_patterns = [
        r'\b(Python|Java|C\+\+|JavaScript|React|Angular|Vue|Node\.js|Flask|Django)\b',
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|Git|SQL|Excel|PowerPoint|Tableau)\b',
        r'\b(SAP|Photoshop|Illustrator|MATLAB|R|AutoCAD|Revit|Office)\b'
    ]
    
    for pattern in tool_patterns:
        matches = re.findall(pattern, text)
        entities["TOOLS"].extend(matches)
    
    # Remove duplicates and sort
    for category in entities:
        entities[category] = sorted(list(set(entities[category])))
    
    return entities

def fallback_extract_entities(text):
    """Fallback method for entity extraction using regex only."""
    entities = {
        "SKILLS": [],
        "COMPANIES": [],
        "EDUCATION": [],
        "TOOLS": []
    }
    
    # Extract skills
    for skill in skills_list:
        if skill and skill.lower() in text.lower():
            # Verify it's a standalone word
            skill_pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(skill_pattern, text, re.IGNORECASE):
                entities["SKILLS"].append(skill)
    
    # Extract company names (simple approach)
    company_pattern = r'\b(Inc\.|LLC|Ltd\.|Corporation|Company|Group)\b'
    company_matches = re.finditer(company_pattern, text)
    
    for match in company_matches:
        # Get the preceding words (likely the company name)
        start_pos = max(0, match.start() - 50)
        fragment = text[start_pos:match.start()].strip()
        words = fragment.split()
        if words:
            # Take up to last 3 words as company name
            company = " ".join(words[-3:])
            entities["COMPANIES"].append(company.strip())
    
    # Extract education terms
    education_patterns = [
        r'\b(Bachelor|Master|MBA|PhD|BSc|MSc|BA|MA|MD|JD)\b',
        r'\b(University|College|School|Institute|Academy)\b',
        r'\b(Degree|Diploma|Certificate)\b'
    ]
    
    for pattern in education_patterns:
        matches = re.findall(pattern, text)
        entities["EDUCATION"].extend(matches)
    
    # Extract tools and technologies
    tool_patterns = [
        r'\b(Python|Java|C\+\+|JavaScript|React|Angular|Vue|Node\.js|Flask|Django)\b',
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|Git|SQL|Excel|PowerPoint|Tableau)\b',
        r'\b(SAP|Photoshop|Illustrator|MATLAB|R|AutoCAD|Revit|Office)\b'
    ]
    
    for pattern in tool_patterns:
        matches = re.findall(pattern, text)
        entities["TOOLS"].extend(matches)
    
    # Remove duplicates and sort
    for category in entities:
        entities[category] = sorted(list(set(entities[category])))
    
    return entities
