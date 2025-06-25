"""
Test script for the MAANG-style ATS Scorer implementation.

This script validates the ATS scoring algorithm against sample resumes and job descriptions.
"""

import os
import sys
import logging
from utils.maang_ats_scorer import calculate_resume_ats_score, test_ats_scorer
from utils.advanced_analyzer import job_specific_ats_score

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample resume for a software engineer
SE_RESUME = """
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

# Sample resume for a data scientist
DS_RESUME = """
JANE SMITH
Data Scientist
jane.smith@example.com | (234) 567-8901 | linkedin.com/in/janesmith

SUMMARY
Data scientist with 3 years of experience in machine learning and statistical analysis.
Expertise in Python, SQL, and ML frameworks with a focus on predictive modeling.

SKILLS
Programming: Python, R, SQL
Machine Learning: PyTorch, TensorFlow, scikit-learn, Natural Language Processing
Data Technologies: Pandas, NumPy, Spark, Hadoop, Tableau, Power BI

EXPERIENCE
Data Scientist | DataInsights Corp | 2022 - Present
- Developed recommendation algorithms increasing user engagement by 25%
- Created predictive models for customer churn with 85% accuracy
- Built data pipelines processing over 1TB of data daily
- Presented analytical findings to executive stakeholders

Junior Data Analyst | Analytics Hub | 2020 - 2022
- Performed exploratory data analysis identifying key business trends
- Developed automated reporting dashboards using Tableau
- Collaborated with cross-functional teams to implement data-driven solutions

EDUCATION
Master of Science in Data Science | Tech University | 2020
Bachelor of Science in Statistics | State University | 2018

CERTIFICATIONS
AWS Certified Data Analytics - Specialty
Microsoft Certified: Azure Data Scientist Associate
"""

# Sample job descriptions
GOOGLE_SE_JOB = """
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

AMAZON_DS_JOB = """
Data Scientist
Amazon Prime Video Analytics

Responsibilities:
- Build and deploy machine learning models to improve content recommendations
- Analyze large datasets to extract actionable insights
- Develop algorithms for customer behavior prediction
- Create dashboards and visualizations to communicate findings
- Collaborate with product and engineering teams to implement data-driven solutions

Requirements:
- Master's or PhD in Computer Science, Statistics, Mathematics, or related field
- 2+ years of experience in data science or machine learning
- Proficiency in Python and SQL
- Experience with ML frameworks such as PyTorch, TensorFlow, or scikit-learn
- Strong understanding of statistical methods and experimental design
- Excellent data visualization and storytelling skills
- AWS certification is a plus
- Experience with big data technologies like Spark or Hadoop
"""

def extract_skills(resume_text):
    """Simple skill extraction from resume text."""
    skill_section = None
    
    # Try to find a skills section
    lines = resume_text.split('\n')
    for i, line in enumerate(lines):
        if line.lower().strip() == "skills":
            skill_section = i
            break
    
    if skill_section is None:
        return []
    
    # Extract skills from the next line(s)
    skills = []
    i = skill_section + 1
    while i < len(lines) and lines[i].strip() and not lines[i].strip().endswith(':'):
        skills_line = lines[i].strip()
        if ':' in skills_line:
            # Handle format like "Category: Skill1, Skill2, Skill3"
            skills_text = skills_line.split(':', 1)[1].strip()
            skills.extend([s.strip() for s in skills_text.split(',') if s.strip()])
        elif ',' in skills_line:
            # Handle comma-separated skills
            skills.extend([s.strip() for s in skills_line.split(',') if s.strip()])
        i += 1
    
    return skills

def test_direct_ats_scoring():
    """Test the ATS scorer directly using the MAANG formula."""
    se_skills = extract_skills(SE_RESUME)
    ds_skills = extract_skills(DS_RESUME)
    
    # Test software engineer resume against Google software engineer job
    logger.info("Testing Software Engineer resume against Google Software Engineer job")
    se_google_result = calculate_resume_ats_score(SE_RESUME, GOOGLE_SE_JOB, se_skills)
    logger.info(f"ATS Score: {se_google_result['ats_score']}")
    logger.info(f"Skills Score (40%): {se_google_result['skill_score']}/40")
    logger.info(f"Experience Score (40%): {se_google_result['experience_score']}/40")
    logger.info(f"Education Score (20%): {se_google_result['education_score']}/20")
    logger.info(f"Skills breakdown: {se_google_result['skill_details']}")
    logger.info("")
    
    # Test data scientist resume against Amazon data scientist job
    logger.info("Testing Data Scientist resume against Amazon Data Scientist job")
    ds_amazon_result = calculate_resume_ats_score(DS_RESUME, AMAZON_DS_JOB, ds_skills)
    logger.info(f"ATS Score: {ds_amazon_result['ats_score']}")
    logger.info(f"Skills Score (40%): {ds_amazon_result['skill_score']}/40")
    logger.info(f"Experience Score (40%): {ds_amazon_result['experience_score']}/40")
    logger.info(f"Education Score (20%): {ds_amazon_result['education_score']}/20")
    logger.info(f"Skills breakdown: {ds_amazon_result['skill_details']}")
    logger.info("")
    
    # Test mismatch: Software Engineer resume against Data Scientist job
    logger.info("Testing Software Engineer resume against Data Scientist job (mismatch)")
    se_ds_result = calculate_resume_ats_score(SE_RESUME, AMAZON_DS_JOB, se_skills)
    logger.info(f"ATS Score: {se_ds_result['ats_score']}")
    logger.info(f"Skills Score (40%): {se_ds_result['skill_score']}/40")
    logger.info(f"Experience Score (40%): {se_ds_result['experience_score']}/40")
    logger.info(f"Education Score (20%): {se_ds_result['education_score']}/20")
    logger.info("")

def test_integrated_ats_scoring():
    """Test the ATS scorer through the advanced_analyzer integration."""
    se_skills = extract_skills(SE_RESUME)
    ds_skills = extract_skills(DS_RESUME)
    
    # Test software engineer resume with advanced_analyzer
    logger.info("Testing Software Engineer resume through advanced_analyzer")
    se_score, se_breakdown = job_specific_ats_score(SE_RESUME, "Software Engineer", se_skills)
    logger.info(f"Overall ATS Score: {se_score}")
    logger.info(f"Score breakdown: {se_breakdown}")
    logger.info("")
    
    # Test data scientist resume with advanced_analyzer
    logger.info("Testing Data Scientist resume through advanced_analyzer")
    ds_score, ds_breakdown = job_specific_ats_score(DS_RESUME, "Data Scientist", ds_skills)
    logger.info(f"Overall ATS Score: {ds_score}")
    logger.info(f"Score breakdown: {ds_breakdown}")
    logger.info("")

if __name__ == "__main__":
    logger.info("Running MAANG ATS Scorer tests")
    
    # Run direct tests
    test_direct_ats_scoring()
    
    # Run integrated tests
    test_integrated_ats_scoring()
    
    logger.info("All tests completed")