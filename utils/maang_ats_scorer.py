"""
MAANG-style ATS Scorer Module

This module implements the ATS scoring algorithm used by major tech companies like
Meta, Apple, Amazon, Netflix, and Google. It provides a more accurate assessment
of resume compatibility with job descriptions.

The scoring breakdown follows:
- Skills Matching (40%): Match skills from resume to job requirements
- Experience Relevance (40%): Based on years + relevant responsibilities
- Education & Certifications (20%): Degree level and relevant certifications

Each component is calculated separately and then combined for the final score.
"""

import re
import logging
from typing import List, Dict, Tuple, Any, Optional

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_required_skills(job_description: str) -> List[str]:
    """Extract required skills from a job description."""
    # Split the job description into lines
    lines = job_description.lower().split('\n')
    
    # Look for requirement sections
    requirements_section = False
    required_skills = []
    
    for line in lines:
        # Check if this line indicates the start of requirements
        if re.search(r'requirements|qualifications|what you.*need|skills|you will need', line):
            requirements_section = True
            continue
            
        # If we're in a requirements section, extract skill-like terms
        if requirements_section:
            # Look for bullet points or numbered lists
            if re.search(r'^\s*[\-\*•]|\d+\.', line):
                # Extract skills that look like technical terms
                skills = re.findall(r'\b([a-z0-9\+\#]+(?:\s?[a-z0-9\+\#]+)*)\b', line)
                for skill in skills:
                    if len(skill) > 2 and not re.match(r'^(and|the|with|for|in|of|to|or|on|at|by|as|an)$', skill):
                        required_skills.append(skill.strip())
                        
            # Check if we've reached the end of the requirements section
            if re.search(r'benefits|perks|why join|about us|we offer', line):
                requirements_section = False
    
    # If we couldn't find a proper requirements section, try a simpler approach
    if not required_skills:
        common_skills = [
            'python', 'java', 'javascript', 'c\+\+', 'c#', 'sql', 'ruby', 'php', 'swift',
            'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'cloud', 'devops', 'agile', 'scrum',
            'git', 'ci/cd', 'machine learning', 'ai', 'data science', 'analytics',
            'hadoop', 'spark', 'big data', 'nosql', 'mongodb', 'postgresql', 'mysql',
            'oracle', 'rest', 'api', 'microservices', 'testing', 'junit', 'selenium'
        ]
        
        # Look for common skills in the job description
        for skill in common_skills:
            if re.search(r'\b' + skill + r'\b', job_description.lower()):
                required_skills.append(skill)
    
    # Remove duplicates
    required_skills = list(set(required_skills))
    
    logger.info(f"Extracted required skills: {required_skills}")
    return required_skills

def calculate_skills_match_score(resume_skills: List[str], job_skills: List[str]) -> Tuple[float, Dict]:
    """Calculate skills match score (40% of total) with detailed breakdown."""
    if not job_skills:
        return 20.0, {"matched": [], "partially_matched": [], "missing": [], "percentage": 50}
    
    # Normalize skills to lowercase for matching
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    job_skills_lower = [skill.lower() for skill in job_skills]
    
    # Initialize counters
    exact_matches = []
    partial_matches = []
    missing_skills = []
    
    # For each required job skill, check if it exists in the resume
    for job_skill in job_skills_lower:
        if job_skill in resume_skills_lower:
            exact_matches.append(job_skill)
        else:
            # Check for partial matches
            partial_match = False
            for resume_skill in resume_skills_lower:
                if job_skill in resume_skill or resume_skill in job_skill:
                    partial_matches.append(job_skill)
                    partial_match = True
                    break
            
            if not partial_match:
                missing_skills.append(job_skill)
    
    # Calculate points
    total_skills = len(job_skills_lower)
    exact_match_points = len(exact_matches) * (1.0 / total_skills)
    partial_match_points = len(partial_matches) * (0.5 / total_skills)
    
    # Calculate the percentage match (0-100)
    match_percentage = (exact_match_points + partial_match_points) * 100
    
    # Calculate the score out of 40 points
    skill_score = (match_percentage / 100) * 40
    
    # Cap the score at 40
    skill_score = min(40, skill_score)
    
    # Return the score and details
    return skill_score, {
        "matched": exact_matches,
        "partially_matched": partial_matches,
        "missing": missing_skills,
        "percentage": match_percentage
    }

def extract_years_of_experience(resume_text: str) -> int:
    """Extract total years of experience from resume."""
    # Look for date ranges in the experience section
    date_ranges = re.findall(r'(\d{4})\s*-\s*(\d{4}|present|current|now)', 
                            resume_text.lower())
    
    total_years = 0
    current_year = 2025  # Current year
    
    for start_year, end_year in date_ranges:
        start = int(start_year)
        
        # Handle current positions
        if end_year.lower() in ['present', 'current', 'now']:
            end = current_year
        else:
            end = int(end_year)
        
        # Calculate years worked
        years_worked = end - start
        
        # Only count reasonable experience durations
        if 0 < years_worked <= 30:  # Reasonable range for work experience
            total_years += years_worked
    
    # If no date ranges found, try to find explicit statements of experience
    if total_years == 0:
        experience_statements = re.findall(
            r'(\d+)\+?\s*(?:years|yrs|yr)(?:\s*of\s*)?(?:experience|exp)',
            resume_text.lower()
        )
        
        if experience_statements:
            # Get the largest mentioned experience
            total_years = max([int(years) for years in experience_statements])
    
    logger.info(f"Extracted years of experience: {total_years}")
    return min(20, total_years)  # Cap at 20 years

def extract_experience_section(resume_text: str) -> str:
    """Extract the experience section from a resume."""
    # Split the resume text into sections
    sections = resume_text.split('\n\n')
    
    # Look for experience section
    experience_section = ""
    in_experience_section = False
    
    for section in sections:
        # Check if this section is the start of experience
        if re.search(r'experience|work history|employment|professional background', 
                    section.lower()):
            in_experience_section = True
            experience_section += section + "\n\n"
        elif in_experience_section:
            # Check if we've reached a new section
            if re.search(r'^(education|skills|certifications|awards|references|projects)', 
                        section.lower()):
                in_experience_section = False
            else:
                experience_section += section + "\n\n"
    
    # If no experience section found, return the whole resume
    if not experience_section:
        return resume_text
    
    return experience_section

def extract_key_responsibilities(job_description: str) -> List[str]:
    """Extract key responsibility keywords from job description."""
    # Split job description into lines
    lines = job_description.lower().split('\n')
    
    # Look for responsibilities section
    responsibilities_section = False
    key_responsibilities = []
    
    for line in lines:
        # Check if this line indicates the start of responsibilities
        if re.search(r'responsibilities|what you.*do|job duties|you will|role|position', line):
            responsibilities_section = True
            continue
            
        # If we're in a responsibilities section, extract terms
        if responsibilities_section:
            # Look for bullet points or numbered lists
            if re.search(r'^\s*[\-\*•]|\d+\.', line):
                # Extract action verbs and key terms
                resp = re.sub(r'^\s*[\-\*•]|\d+\.', '', line).strip()
                if resp:
                    key_responsibilities.append(resp)
                        
            # Check if we've reached the end of the responsibilities section
            if re.search(r'requirements|qualifications|what you.*need|skills', line):
                responsibilities_section = False
    
    # If we couldn't find a proper responsibilities section, try extracting action verbs
    if not key_responsibilities:
        # Common action verbs used in job descriptions
        action_verbs = [
            'develop', 'design', 'create', 'implement', 'manage', 'lead', 'analyze',
            'build', 'maintain', 'collaborate', 'coordinate', 'test', 'debug', 'optimize',
            'research', 'evaluate', 'present', 'communicate', 'report', 'monitor'
        ]
        
        for line in lines:
            for verb in action_verbs:
                if re.search(r'\b' + verb + r'\b', line.lower()):
                    key_responsibilities.append(line.strip())
                    break
    
    # Remove duplicates and long entries
    unique_responsibilities = []
    for resp in key_responsibilities:
        if resp not in unique_responsibilities and len(resp) < 200:
            unique_responsibilities.append(resp)
    
    logger.info(f"Extracted key responsibilities: {unique_responsibilities[:5]}")
    return unique_responsibilities

def calculate_experience_relevance_score(resume_text: str, job_description: str) -> Tuple[float, Dict]:
    """Calculate experience relevance score (40% of total)."""
    # Extract years of experience (worth up to 20 points)
    years = extract_years_of_experience(resume_text)
    years_score = min(20, years)
    
    # Extract experience section from resume
    experience_section = extract_experience_section(resume_text)
    
    # Extract key responsibilities from job description
    key_responsibilities = extract_key_responsibilities(job_description)
    
    # Check how many responsibilities are mentioned in the experience section
    matched_responsibilities = []
    
    for resp in key_responsibilities:
        # Check for key phrases from the responsibility
        key_phrases = [phrase for phrase in resp.split() if len(phrase) > 3]
        
        for phrase in key_phrases:
            if phrase in experience_section.lower():
                matched_responsibilities.append(resp)
                break
    
    # Calculate responsibility match score (worth up to 20 points)
    resp_match_percentage = len(matched_responsibilities) / max(1, len(key_responsibilities))
    resp_score = min(20, resp_match_percentage * 20)
    
    # Calculate total experience score
    experience_score = years_score + resp_score
    
    # Return the score and details
    return experience_score, {
        "years_experience": years,
        "years_score": years_score,
        "responsibility_match": resp_match_percentage * 100,
        "responsibility_score": resp_score,
        "matched_responsibilities": matched_responsibilities[:5]
    }

def extract_education_level(resume_text: str) -> Tuple[str, float]:
    """Extract highest education level and corresponding score."""
    # Look for degree mentions in the resume
    phd_match = re.search(r'ph\.?d|doctor(?:ate)?|d\.phil', resume_text.lower())
    masters_match = re.search(r'master|ms\.?|m\.s|m\.b\.a|mba|m\.eng|m\.ed', resume_text.lower())
    bachelors_match = re.search(r'bachelor|ba\.?|b\.s|b\.a|b\.eng|b\.ed', resume_text.lower())
    associates_match = re.search(r'associate|a\.s|a\.a', resume_text.lower())
    
    # Determine highest education level
    if phd_match:
        return "PhD", 20.0
    elif masters_match:
        return "Master's", 15.0
    elif bachelors_match:
        return "Bachelor's", 10.0
    elif associates_match:
        return "Associate's", 5.0
    else:
        return "Not specified", 0.0

def extract_certifications(resume_text: str) -> List[str]:
    """Extract certifications from resume text."""
    # Look for certification section
    cert_section = ""
    lines = resume_text.split('\n')
    
    in_cert_section = False
    for line in lines:
        if re.search(r'certification|certificate', line.lower()):
            in_cert_section = True
            cert_section += line + "\n"
        elif in_cert_section:
            if re.search(r'^(education|skills|experience|awards|references|projects)', 
                        line.lower()):
                in_cert_section = False
            else:
                cert_section += line + "\n"
    
    # Common certification keywords to look for
    cert_keywords = [
        'certified', 'certificate', 'certification', 'credential', 'licensed',
        'aws', 'azure', 'google cloud', 'pmp', 'scrum', 'cissp', 'comptia',
        'itil', 'prince2', 'six sigma', 'cisa', 'cism', 'ceh', 'mcsa', 'mcse',
        'ccna', 'ccnp', 'cka', 'ckad', 'rhce', 'rhcsa', 'oracle', 'salesforce'
    ]
    
    # Extract certifications based on keywords
    certifications = []
    
    # First check cert section if available
    if cert_section:
        # Extract certification mentions (bullet points or new lines)
        cert_mentions = re.findall(r'(?:^\s*[\-\*•]|\d+\.|\n)([^\n]+)', cert_section)
        for mention in cert_mentions:
            for keyword in cert_keywords:
                if keyword.lower() in mention.lower():
                    certifications.append(mention.strip())
                    break
    
    # If no certifications found in a section, check the entire resume
    if not certifications:
        # Look for mentions near certification keywords
        for keyword in cert_keywords:
            pattern = r'(' + keyword + r'[^.!?\n]*)'
            matches = re.findall(pattern, resume_text.lower())
            certifications.extend([match.strip() for match in matches])
    
    # Remove duplicates
    unique_certs = []
    for cert in certifications:
        if cert not in unique_certs:
            unique_certs.append(cert)
    
    logger.info(f"Extracted certifications: {unique_certs}")
    return unique_certs

def calculate_education_certification_score(resume_text: str, job_description: str) -> Tuple[float, Dict]:
    """Calculate education and certification score (20% of total)."""
    # Extract education level (worth up to 15 points)
    education_level, education_score = extract_education_level(resume_text)
    
    # Extract certifications
    certifications = extract_certifications(resume_text)
    
    # Calculate certification score (worth up to 5 points)
    cert_score = min(5.0, len(certifications) * 1.0)
    
    # Check if certifications are mentioned in job description
    relevant_certs = []
    if certifications:
        for cert in certifications:
            for word in cert.lower().split():
                if len(word) > 3 and word in job_description.lower():
                    relevant_certs.append(cert)
                    break
    
    # Bonus for relevant certifications
    if relevant_certs:
        cert_score = min(5.0, cert_score + 1.0)
    
    # Calculate total education score
    education_cert_score = education_score + cert_score
    
    # Return the score and details
    return education_cert_score, {
        "education_level": education_level,
        "education_score": education_score,
        "certification_count": len(certifications),
        "certification_score": cert_score,
        "certifications": certifications[:5],
        "relevant_certifications": relevant_certs
    }

def calculate_resume_ats_score(resume_text: str, job_description: str, resume_skills: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Calculate the ATS score for a resume based on the MAANG formula.
    
    Args:
        resume_text: The extracted text from the resume
        job_description: The job description to match against
        resume_skills: Optional pre-extracted skills from the resume
        
    Returns:
        A dictionary containing the overall score and detailed breakdown
    """
    logger.info("Calculating MAANG-style ATS score...")
    
    # Extract job skills if not provided
    job_skills = extract_required_skills(job_description)
    
    # If resume skills not provided, use job skills for approximate matching
    if not resume_skills:
        resume_skills = []
        for skill in job_skills:
            if skill.lower() in resume_text.lower():
                resume_skills.append(skill)
    
    # Calculate each component of the score
    skill_score, skill_details = calculate_skills_match_score(resume_skills, job_skills)
    experience_score, experience_details = calculate_experience_relevance_score(resume_text, job_description)
    education_score, education_details = calculate_education_certification_score(resume_text, job_description)
    
    # Calculate the overall score (out of 100)
    overall_score = skill_score + experience_score + education_score
    
    # Log the results
    logger.info(f"Skill Score: {skill_score}/40")
    logger.info(f"Experience Score: {experience_score}/40")
    logger.info(f"Education Score: {education_score}/20")
    logger.info(f"Overall ATS Score: {overall_score}")
    
    # Return detailed results
    return {
        "ats_score": round(overall_score),
        "skill_score": round(skill_score, 1),
        "experience_score": round(experience_score, 1),
        "education_score": round(education_score, 1),
        "skill_details": skill_details,
        "experience_details": experience_details,
        "education_details": education_details,
        "skill_percentage": round(skill_score / 40 * 100, 1),
        "experience_percentage": round(experience_score / 40 * 100, 1),
        "education_percentage": round(education_score / 20 * 100, 1)
    }

def test_ats_scorer():
    """Run tests to validate the ATS scorer against sample job descriptions."""
    # Sample resume for a software engineer
    se_resume = """
    JOHN DOE
    Software Engineer
    john.doe@example.com | (123) 456-7890 | linkedin.com/in/johndoe

    SUMMARY
    Experienced software engineer with 5 years of expertise in cloud-based solutions and microservices architecture. 
    Skilled in Python, Java, and Go with a focus on scalable, efficient solutions.

    SKILLS
    Programming Languages: Python, Java, Go, JavaScript
    Cloud Technologies: Google Cloud Platform, AWS, Kubernetes, Docker
    Tools & Frameworks: Django, Spring Boot, React, Git, CI/CD, Jenkins

    EXPERIENCE
    Senior Software Engineer | TechCorp Inc. | 2020 - Present
    - Developed and maintained cloud microservices using Python and GCP
    - Implemented CI/CD pipelines reducing deployment time by 40%
    - Led a team of 5 engineers to deliver a critical customer-facing application
    - Optimized database queries improving response time by 30%

    Software Developer | CodeWorks LLC | 2018 - 2020
    - Built RESTful APIs using Java Spring Boot
    - Collaborated with product managers to define and implement features
    - Conducted code reviews and mentored junior developers
    - Implemented automated testing increasing code coverage by 25%

    EDUCATION
    Master of Science in Computer Science | University of Technology | 2018
    Bachelor of Science in Computer Engineering | State University | 2016

    CERTIFICATIONS
    Google Cloud Professional Developer
    Oracle Certified Java Professional
    """

    # Sample job description for a software engineer
    se_job = """
    Software Engineer
    Google Cloud Platform

    Responsibilities:
    - Design, develop, and maintain scalable cloud services and infrastructure
    - Write clean, efficient code in languages like Python, Java, or Go
    - Collaborate with cross-functional teams to define and implement new features
    - Debug and solve complex technical issues
    - Participate in code reviews and mentor junior engineers

    Requirements:
    - Bachelor's degree in Computer Science or related field, Master's preferred
    - 3+ years of software development experience
    - Strong knowledge of data structures, algorithms, and software design
    - Proficiency in Python, Java, or Go
    - Experience with cloud technologies (preferably GCP)
    - Knowledge of distributed systems and microservices architecture
    - Excellent problem-solving and communication skills
    - Experience with CI/CD pipelines and DevOps practices
    """

    # Calculate ATS score
    result = calculate_resume_ats_score(se_resume, se_job)
    
    # Log the results
    logger.info(f"Test ATS Score: {result['ats_score']}")
    logger.info(f"Test Skills Score: {result['skill_score']}/40")
    logger.info(f"Test Experience Score: {result['experience_score']}/40")
    logger.info(f"Test Education Score: {result['education_score']}/20")
    
    return result

if __name__ == "__main__":
    test_ats_scorer()