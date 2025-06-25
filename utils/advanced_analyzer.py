"""
Advanced Resume Analyzer Module
Provides functions for detailed resume analysis, job matching, and ATS scoring.
Using MAANG (Meta, Apple, Amazon, Netflix, Google) style ATS scoring algorithm.
"""
import re
import logging
import random
from collections import Counter
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    USE_SKLEARN = True
except ImportError:
    logging.warning("Using fallback keyword matching for ATS scoring")
    USE_SKLEARN = False

# Import the MAANG ATS scorer
try:
    from utils.maang_ats_scorer import (
        calculate_resume_ats_score,
        extract_required_skills,
        extract_years_of_experience,
        extract_education_level,
        extract_certifications
    )
    MAANG_SCORER_LOADED = True
except Exception as e:
    logging.error(f"Error loading MAANG ATS scorer: {str(e)}")
    MAANG_SCORER_LOADED = False

# Load standard job descriptions and requirements
try:
    import pandas as pd
    job_data = pd.read_csv('attached_assets/job_title_des.csv')
    job_titles = job_data['Job Title'].tolist()
    job_descriptions = job_data['Job Description'].tolist()
    JOB_DATA_LOADED = True
except Exception as e:
    logging.error(f"Error loading job data: {str(e)}")
    job_titles = []
    job_descriptions = []
    JOB_DATA_LOADED = False

# Common keywords for different job roles
JOB_KEYWORDS = {
    'Software Engineer': ['python', 'java', 'javascript', 'c++', 'sql', 'algorithms', 'data structures', 
                         'software development', 'git', 'agile', 'object-oriented', 'programming'],
    'Data Scientist': ['python', 'r', 'machine learning', 'statistics', 'data analysis', 
                      'sql', 'tableau', 'deep learning', 'pandas', 'numpy', 'scikit-learn'],
    'Product Manager': ['product development', 'agile', 'scrum', 'user experience', 'market research',
                      'roadmap', 'stakeholder', 'kpi', 'metrics', 'strategy'],
    'UX Designer': ['user experience', 'wireframes', 'prototyping', 'usability', 'figma', 'sketch',
                  'adobe xd', 'user research', 'interaction design', 'information architecture'],
    'Marketing Manager': ['marketing strategy', 'digital marketing', 'social media', 'seo', 'campaign management',
                        'analytics', 'content marketing', 'brand management', 'market research']
}

def fuzzy_match_score(keyword, text, threshold=0.8):
    """Calculate fuzzy match score for a keyword in text."""
    # Simple implementation without external dependencies
    keyword = keyword.lower()
    text = text.lower()
    
    # Exact match
    if keyword in text:
        return 1.0
    
    # Check for partial matches
    words = re.findall(r'\b\w+\b', text)
    for word in words:
        if keyword in word or word in keyword:
            # Calculate similarity based on length
            overlap = len(set(keyword) & set(word))
            total = len(set(keyword) | set(word))
            if total > 0:
                similarity = overlap / total
                if similarity >= threshold:
                    return similarity
    
    return 0.0

def calculate_job_match_scores(resume_text, skills_list=None):
    """Calculate how well a resume matches different job roles."""
    if not resume_text:
        return []
    
    resume_text = resume_text.lower()
    results = []
    
    # If we have skills from the resume, use them to enhance matching
    extracted_skills = skills_list or []
    skills_text = " ".join(extracted_skills).lower()
    
    for job_title, keywords in JOB_KEYWORDS.items():
        matches = 0
        total_keywords = len(keywords)
        
        for keyword in keywords:
            # Check both resume text and extracted skills
            score = max(
                fuzzy_match_score(keyword, resume_text),
                fuzzy_match_score(keyword, skills_text)
            )
            matches += score
        
        # Calculate percentage match
        match_percentage = (matches / total_keywords) * 100 if total_keywords > 0 else 0
        results.append({
            'title': job_title,
            'score': round(match_percentage, 1),
            'keywords': keywords
        })
    
    # Sort by score, descending
    return sorted(results, key=lambda x: x['score'], reverse=True)

def calculate_ats_score(resume_text, job_title, skills_list=None):
    """
    Calculate an ATS compatibility score for a resume against a specific job role.
    
    Uses the MAANG (Meta, Apple, Amazon, Netflix, Google) style ATS scoring algorithm:
    - Skills Matching (40%): Match resume skills against job requirements
    - Experience Relevance (40%): Based on years + relevant responsibilities
    - Education & Certifications (20%): Degree level and relevant certifications
    """
    if not resume_text or not job_title:
        return 65  # Default middle score
    
    # Get job description for the job title
    job_description = ""
    
    # Try to find a matching job title in our dataset
    if job_titles and job_descriptions:
        for i, title in enumerate(job_titles):
            if job_title.lower() in title.lower() or title.lower() in job_title.lower():
                job_description = job_descriptions[i]
                break
    
    # If no job description found, create one based on keywords
    if not job_description:
        for title, keywords in JOB_KEYWORDS.items():
            if job_title.lower() in title.lower() or title.lower() in job_title.lower():
                # Create a simple job description from keywords
                responsibilities = []
                requirements = []
                
                for keyword in keywords:
                    if random.random() < 0.5:
                        verb = random.choice(['Develop', 'Create', 'Implement', 'Manage', 'Analyze', 'Design'])
                        responsibilities.append(f"{verb} solutions using {keyword}")
                    else:
                        requirements.append(f"Experience with {keyword}")
                
                job_description = f"""
                {job_title}
                
                Responsibilities:
                {chr(10).join(['- ' + r for r in responsibilities])}
                
                Requirements:
                {chr(10).join(['- ' + r for r in requirements])}
                """
                break
    
    # If still no job description, use a generic one
    if not job_description:
        job_description = f"""
        {job_title}
        
        Responsibilities:
        - Develop and implement solutions
        - Collaborate with cross-functional teams
        - Analyze and solve complex problems
        - Communicate effectively with stakeholders
        
        Requirements:
        - Experience in relevant field
        - Strong problem-solving abilities
        - Excellent communication skills
        - Technical expertise in relevant areas
        """
    
    # Use the MAANG ATS scorer if available
    if MAANG_SCORER_LOADED:
        try:
            # Extract skills from the resume if not provided
            if skills_list is None:
                # Simple skill extraction from resume
                skills_section = re.search(r'(?:skills|technical skills|core competencies):(.*?)(?:\n\n|\Z)', 
                                         resume_text, re.IGNORECASE | re.DOTALL)
                
                if skills_section:
                    skills_text = skills_section.group(1)
                    skills_list = [s.strip() for s in re.split(r'[,•|\n-]', skills_text) if s.strip()]
                else:
                    skills_list = []
            
            # Use the MAANG ATS scoring function
            result = calculate_resume_ats_score(resume_text, job_description, skills_list)
            
            # Return the overall ATS score
            return result["ats_score"]
            
        except Exception as e:
            logging.error(f"Error using MAANG ATS scorer: {str(e)}")
            # Fall back to the original method if there's an error
    
    # Legacy scoring method (fallback)
    resume_text = resume_text.lower()
    job_keywords = []
    
    # Get keywords for the job title
    for title, keywords in JOB_KEYWORDS.items():
        if job_title.lower() in title.lower() or title.lower() in job_title.lower():
            job_keywords = keywords
            break
    
    if not job_keywords and job_titles and job_descriptions:
        # Extract keywords from the job description
        desc = job_description.lower()
        potential_keywords = re.findall(r'\b\w+\b', desc)
        word_freq = Counter(potential_keywords)
        # Filter out common words
        stop_words = {'and', 'the', 'to', 'of', 'a', 'in', 'for', 'with', 'on', 'at', 'from', 'by', 'is', 'are'}
        job_keywords = [word for word, count in word_freq.most_common(15) if word not in stop_words and len(word) > 3]
    
    if not job_keywords:
        # Fallback to general professional keywords
        job_keywords = ['experience', 'skills', 'project', 'team', 'develop', 'manage', 'analyze', 
                        'create', 'implement', 'collaborate', 'lead', 'organize', 'communicate']
    
    # Calculate keyword matches
    keyword_matches = 0
    for keyword in job_keywords:
        if fuzzy_match_score(keyword, resume_text, threshold=0.7) > 0:
            keyword_matches += 1
    
    keyword_score = (keyword_matches / len(job_keywords)) * 100 if job_keywords else 50
    
    # Check for contact information
    contact_score = 0
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
        contact_score += 10  # Email found
    if re.search(r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', resume_text):
        contact_score += 10  # Phone number found
    
    # Check for formatting and structure
    structure_score = 0
    
    # Check for section headers
    sections = ['experience', 'education', 'skills', 'projects', 'summary', 'objective']
    found_sections = 0
    for section in sections:
        if re.search(rf'\b{section}\b', resume_text, re.IGNORECASE):
            found_sections += 1
    
    structure_score += min(30, found_sections * 5)  # Up to 30 points for sections
    
    # Calculate final score (weighted average)
    final_score = 0.6 * keyword_score + 0.2 * contact_score + 0.2 * structure_score
    
    # Ensure score is between 0-100
    return max(0, min(100, final_score))

def get_improvement_suggestions(resume_text, job_title, skills_list=None):
    """
    Generate improvement suggestions based on resume and target job.
    Using the MAANG ATS scoring breakdown for more targeted suggestions.
    """
    if not resume_text or not job_title:
        return ["Add more specific skills relevant to your target role.",
                "Include quantifiable achievements in your experience section.",
                "Ensure your contact information is clearly visible.",
                "Add a concise professional summary at the top."]
    
    # Get job description for the job title
    job_description = ""
    
    # Try to find a matching job title in our dataset
    if job_titles and job_descriptions:
        for i, title in enumerate(job_titles):
            if job_title.lower() in title.lower() or title.lower() in job_title.lower():
                job_description = job_descriptions[i]
                break
    
    # If no job description found, create one based on keywords
    if not job_description:
        for title, keywords in JOB_KEYWORDS.items():
            if job_title.lower() in title.lower() or title.lower() in job_title.lower():
                # Create a simple job description from keywords
                responsibilities = []
                requirements = []
                
                for keyword in keywords:
                    if random.random() < 0.5:
                        verb = random.choice(['Develop', 'Create', 'Implement', 'Manage', 'Analyze', 'Design'])
                        responsibilities.append(f"{verb} solutions using {keyword}")
                    else:
                        requirements.append(f"Experience with {keyword}")
                
                job_description = f"""
                {job_title}
                
                Responsibilities:
                {chr(10).join(['- ' + r for r in responsibilities])}
                
                Requirements:
                {chr(10).join(['- ' + r for r in requirements])}
                """
                break
    
    # If still no job description, use a generic one
    if not job_description:
        job_description = f"""
        {job_title}
        
        Responsibilities:
        - Develop and implement solutions
        - Collaborate with cross-functional teams
        - Analyze and solve complex problems
        - Communicate effectively with stakeholders
        
        Requirements:
        - Experience in relevant field
        - Strong problem-solving abilities
        - Excellent communication skills
        - Technical expertise in relevant areas
        """
    
    # Try to use MAANG ATS scorer for detailed breakdown
    if MAANG_SCORER_LOADED:
        try:
            # Extract skills from the resume if not provided
            if skills_list is None:
                # Simple skill extraction from resume
                skills_section = re.search(r'(?:skills|technical skills|core competencies):(.*?)(?:\n\n|\Z)', 
                                          resume_text, re.IGNORECASE | re.DOTALL)
                
                if skills_section:
                    skills_text = skills_section.group(1)
                    skills_list = [s.strip() for s in re.split(r'[,•|\n-]', skills_text) if s.strip()]
                else:
                    skills_list = []
            
            # Get full ATS score breakdown
            result = calculate_resume_ats_score(resume_text, job_description, skills_list)
            
            # Generate targeted suggestions based on the detailed breakdown
            suggestions = []
            
            # 1. Skills-based suggestions (based on skills_details)
            skill_details = result.get("skill_details", {})
            missing_skills = skill_details.get("missing", [])
            partial_skills = skill_details.get("partial", [])
            
            if missing_skills:
                if len(missing_skills) > 3:
                    suggestions.append(f"Skills Gap: Add these key skills missing from your resume: {', '.join(missing_skills[:3])} and others required for {job_title} roles.")
                else:
                    suggestions.append(f"Skills Gap: Add these key skills missing from your resume: {', '.join(missing_skills)}.")
            
            # 2. Experience-based suggestions (based on experience_details)
            experience_details = result.get("experience_details", {})
            years = experience_details.get("years_of_experience", 0)
            matched_resp = experience_details.get("matched_responsibilities", [])
            total_resp = experience_details.get("total_responsibilities", 0)
            
            if years < 3:
                suggestions.append(f"Experience Detail: Emphasize your years of experience more clearly. ATS systems will look for this specifically.")
            
            if total_resp > 0 and len(matched_resp) < total_resp * 0.5:
                suggestions.append(f"Responsibilities: Use more job-specific responsibility terms like '{', '.join(matched_resp[:3]) if matched_resp else 'managing, developing, implementing'}' in your experience section.")
            
            # 3. Education-based suggestions
            education_details = result.get("education_details", {})
            education_level = education_details.get("education_level", "None detected")
            certifications = education_details.get("certifications", [])
            
            if education_level == "None detected":
                suggestions.append("Education Gap: Make your education details more prominent, as ATS systems specifically score this section.")
            
            if not certifications:
                suggestions.append(f"Certification Value: Consider adding relevant certifications for {job_title} positions to boost your ATS score.")
            
            # If we don't have enough suggestions, add general ones
            if len(suggestions) < 5:
                general_suggestions = [
                    f"Structure: Organize your resume with clear section headers (Skills, Experience, Education).",
                    f"Keyword Alignment: Tailor your resume specifically for {job_title} positions using exact terms from job descriptions.",
                    "Quantifiable Impact: Add metrics and percentages to demonstrate the impact of your work.",
                    "Consistent Formatting: Use simple, consistent formatting that ATS systems can easily parse.",
                    "Action Verbs: Start bullet points with strong action verbs like 'Developed', 'Managed', 'Created'."
                ]
                
                # Add general suggestions that aren't already included
                for suggestion in general_suggestions:
                    if len(suggestions) >= 5:
                        break
                    
                    # Simple way to avoid duplicates by checking first few words
                    is_duplicate = False
                    suggestion_start = suggestion.split(":")[0].lower()
                    for existing in suggestions:
                        if suggestion_start in existing.lower():
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        suggestions.append(suggestion)
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logging.error(f"Error generating MAANG ATS suggestions: {str(e)}")
            # Fall back to the original method if there's an error
    
    # Legacy method (fallback)
    suggestions = []
    resume_text = resume_text.lower()
    
    # Get keywords for the job title
    job_keywords = []
    for title, keywords in JOB_KEYWORDS.items():
        if job_title.lower() in title.lower() or title.lower() in job_title.lower():
            job_keywords = keywords
            break
    
    # Check for missing keywords
    missing_keywords = []
    for keyword in job_keywords:
        if fuzzy_match_score(keyword, resume_text, threshold=0.7) == 0:
            missing_keywords.append(keyword)
    
    if missing_keywords:
        if len(missing_keywords) > 3:
            suggestions.append(f"Consider adding these relevant keywords: {', '.join(missing_keywords[:3])} and others related to {job_title}.")
        else:
            suggestions.append(f"Consider adding these relevant keywords: {', '.join(missing_keywords)}.")
    
    # Check for contact information
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
        suggestions.append("Make sure your email address is clearly visible.")
    
    if not re.search(r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', resume_text):
        suggestions.append("Include your phone number for recruiters to contact you.")
    
    # Check for common sections
    sections = ['experience', 'education', 'skills', 'projects', 'summary', 'objective']
    missing_sections = []
    for section in sections[:4]:  # First 4 are most important
        if not re.search(rf'\b{section}\b', resume_text, re.IGNORECASE):
            missing_sections.append(section.title())
    
    if missing_sections:
        suggestions.append(f"Add these important sections to your resume: {', '.join(missing_sections)}.")
    
    # Check for action verbs
    action_verbs = ['managed', 'developed', 'created', 'implemented', 'designed', 'led', 'analyzed']
    verb_count = sum(1 for verb in action_verbs if re.search(rf'\b{verb}\b', resume_text, re.IGNORECASE))
    
    if verb_count < 3:
        suggestions.append("Use more action verbs like 'Developed', 'Managed', 'Created', 'Implemented' to describe your accomplishments.")
    
    # If we have few suggestions, add some general ones
    if len(suggestions) < 3:
        general_suggestions = [
            f"Tailor your resume specifically for {job_title} positions by highlighting relevant experience.",
            "Quantify your achievements with numbers and percentages where possible.",
            "Keep your resume concise - ideally 1-2 pages depending on experience level.",
            "Ensure consistent formatting throughout your document.",
            "Consider adding a skills section with bullet points for easy scanning."
        ]
        suggestions.extend(random.sample(general_suggestions, min(3, len(general_suggestions))))
    
    return suggestions[:5]  # Return top 5 suggestions

def analyze_resume(resume_text, skills_list=None):
    """
    Perform comprehensive resume analysis for job matching and ATS scoring.
    
    Uses the MAANG (Meta, Apple, Amazon, Netflix, Google) style ATS scoring algorithm:
    - Skills Matching (40%): Match resume skills against job requirements
    - Experience Relevance (40%): Based on years + relevant responsibilities
    - Education & Certifications (20%): Degree level and relevant certifications
    """
    if not resume_text:
        return {
            'ats_score': 65,
            'top_job': 'General Professional',
            'job_matches': [],
            'improvement_suggestions': [
                "Add more specific skills relevant to your target roles.",
                "Include quantifiable achievements in your experience section.",
                "Ensure your contact information is clearly visible.",
                "Add a concise professional summary at the top."
            ]
        }
    
    # Calculate job matches
    job_matches = calculate_job_match_scores(resume_text, skills_list)
    
    # Get top job match
    top_job = job_matches[0]['title'] if job_matches else 'General Professional'
    
    # Calculate ATS score for top job match
    ats_score = calculate_ats_score(resume_text, top_job, skills_list)
    
    # Get job description for the top job match
    job_description = ""
    if job_titles and job_descriptions:
        for i, title in enumerate(job_titles):
            if top_job.lower() in title.lower() or title.lower() in top_job.lower():
                job_description = job_descriptions[i]
                break
    
    # Get detailed ATS score breakdown if MAANG scoring is available
    score_breakdown = {}
    if MAANG_SCORER_LOADED and job_description:
        try:
            result = calculate_resume_ats_score(resume_text, job_description, skills_list)
            score_breakdown = {
                'skill_score': result.get('skill_score', 0),
                'experience_score': result.get('experience_score', 0),
                'education_score': result.get('education_score', 0),
                'skill_percentage': result.get('skill_percentage', 0),
                'experience_percentage': result.get('experience_percentage', 0),
                'education_percentage': result.get('education_percentage', 0)
            }
        except Exception as e:
            logging.error(f"Error getting detailed ATS score breakdown: {str(e)}")
    
    # Generate improvement suggestions with skills list
    suggestions = get_improvement_suggestions(resume_text, top_job, skills_list)
    
    result = {
        'ats_score': ats_score,
        'top_job': top_job,
        'job_matches': job_matches,
        'improvement_suggestions': suggestions
    }
    
    # Add score breakdown if available
    if score_breakdown:
        result['score_breakdown'] = score_breakdown
    
    return result

def job_specific_ats_score(resume_text, job_title, skills_list=None):
    """
    Calculate ATS score for a specific job title with detailed breakdown.
    
    Returns a tuple (score, breakdown_dict) where breakdown_dict contains the detailed
    scoring components based on the MAANG ATS formula.
    """
    # Calculate the ATS score
    ats_score = calculate_ats_score(resume_text, job_title, skills_list)
    
    # Get job description for the job title
    job_description = ""
    if job_titles and job_descriptions:
        for i, title in enumerate(job_titles):
            if job_title.lower() in title.lower() or title.lower() in job_title.lower():
                job_description = job_descriptions[i]
                break
    
    # Try to get detailed score breakdown if MAANG scoring is available
    score_breakdown = {}
    if MAANG_SCORER_LOADED and job_description:
        try:
            result = calculate_resume_ats_score(resume_text, job_description, skills_list)
            score_breakdown = {
                'overall_score': result.get('ats_score', ats_score),
                'skill_score': result.get('skill_score', 0),
                'experience_score': result.get('experience_score', 0),
                'education_score': result.get('education_score', 0),
                'skill_percentage': result.get('skill_percentage', 0),
                'experience_percentage': result.get('experience_percentage', 0),
                'education_percentage': result.get('education_percentage', 0),
                # Additional details if available
                'skill_details': result.get('skill_details', {}),
                'experience_details': result.get('experience_details', {}),
                'education_details': result.get('education_details', {})
            }
            # Use the more accurate score if available
            ats_score = result.get('ats_score', ats_score)
        except Exception as e:
            logging.error(f"Error getting detailed job-specific ATS score: {str(e)}")
    
    return ats_score, score_breakdown