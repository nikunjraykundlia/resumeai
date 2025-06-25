"""
Google AI API Helper
Provides functions for resume analysis, improvement suggestions, and ATS scoring
using Google API Studio.
"""

import os
import json
import logging
import requests
from typing import List, Dict, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google AI API configuration
GOOGLE_API_KEY = "AIzaSyC4m5fPvWJ48nJWtTNNPDmU8H76ce2IfCs"
# Use v1 API for Gemini
GOOGLE_AI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-pro:generateContent"

def call_google_ai_api(prompt: str, response_format: str = None) -> Dict[str, Any]:
    """
    Call the Google AI API with the given prompt.
    
    Args:
        prompt: The prompt to send to the API
        response_format: Optional format (text or json)
        
    Returns:
        The parsed response or an error message
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "topK": 32,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }
    
    # Add response format if specified
    if response_format == "json":
        payload["generationConfig"]["responseSchema"] = {"type": "json"}
    
    try:
        # For debugging - log the API URL
        logger.info(f"Making API request to: {GOOGLE_AI_URL}")
        
        # Make the API request
        response = requests.post(
            f"{GOOGLE_AI_URL}?key={GOOGLE_API_KEY}",
            headers=headers,
            json=payload
        )
        
        # Log the response status for debugging
        logger.info(f"Google API response status: {response.status_code}")
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            logger.info("Received successful response from Google AI API")
            
            # Parse the response structure - check for different possible response formats
            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0]["content"]
                if "parts" in content and len(content["parts"]) > 0:
                    response_text = content["parts"][0]["text"]
                    
                    # If JSON was requested, parse the response
                    if response_format == "json":
                        try:
                            return json.loads(response_text)
                        except json.JSONDecodeError:
                            logger.error("Failed to parse JSON response from Google AI API")
                            return {"error": "Invalid JSON response"}
                    
                    return response_text
            
            # Fallback - try direct parsing for different response structure
            if "text" in result:
                return result["text"]
                
            logger.error(f"Unexpected response structure: {result}")
            return {"error": "Unexpected response structure"}
        else:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            return {"error": f"API request failed: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Error calling Google AI API: {str(e)}")
        return {"error": f"Error calling Google AI API: {str(e)}"}

def generate_improvement_suggestions(resume_text: str, job_description: str, extracted_skills: List[str]) -> Union[str, Dict[str, Any]]:
    """
    Generate personalized improvement suggestions for a resume based on a job description.
    
    Args:
        resume_text: The text content of the resume
        job_description: The job description to compare against
        extracted_skills: List of skills extracted from the resume
        
    Returns:
        A string containing improvement suggestions
    """
    try:
        # Format our prompt with resume and job details
        prompt = f"""You are a professional resume analyzer and career coach. Analyze this resume against the target job description and provide specific, actionable improvement suggestions.

RESUME:
{resume_text[:2000]}  # Limit size for token constraints

JOB DESCRIPTION:
{job_description[:1000]}  # Limit size for token constraints

CANDIDATE SKILLS:
{', '.join(extracted_skills)}

Provide 5 specific, detailed improvement suggestions that would help this resume better match the job description. Focus on:
1. Content gaps between resume and job requirements
2. Skills presentation and evidence
3. Achievements and quantifiable results
4. Resume structure and formatting
5. Language and keyword optimization

For each suggestion, provide the specific issue and an actionable solution. Be constructive, specific, and detailed.
"""

        # Call the Google AI API
        response = call_google_ai_api(prompt)
        
        # If the response is a dictionary with an error, return the fallback
        if isinstance(response, dict) and "error" in response:
            return fallback_improvement_suggestions()
            
        return response
        
    except Exception as e:
        logger.error(f"Error generating improvement suggestions: {str(e)}")
        return fallback_improvement_suggestions()

def fallback_improvement_suggestions() -> str:
    """Fallback method for when the API is not available"""
    return """Here are some suggestions to improve your resume:

1. Add more quantifiable achievements to demonstrate your impact
2. Ensure your skills section directly matches keywords from the job description
3. Use strong action verbs at the beginning of your bullet points
4. Maintain consistent formatting and structure throughout your resume
5. Tailor your professional summary to highlight relevant experience for the target role"""

def calculate_ats_score(resume_text: str, job_description: str, extracted_skills: List[str]) -> float:
    """
    Calculate an ATS compatibility score for a resume against a job description.
    
    Args:
        resume_text: The text content of the resume
        job_description: The job description to compare against
        extracted_skills: List of skills extracted from the resume
        
    Returns:
        A score from 0-100 indicating ATS compatibility
    """
    try:
        # Format our prompt
        prompt = f"""Analyze how well this resume would perform in an Applicant Tracking System (ATS) for the given job description.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:1000]}

CANDIDATE SKILLS:
{', '.join(extracted_skills)}

Calculate an ATS compatibility score from 0-100 based on:
1. Keyword matching (40%): How well the resume's keywords match the job description
2. Skills alignment (30%): How the candidate's skills match required skills
3. Experience relevance (20%): How relevant the experience is to the job
4. Format & readability (10%): How well-structured and parseable the resume is

Provide a JSON response with the following structure:
{{
  "overall_score": 85,
  "keyword_matching_score": 80,
  "skills_alignment_score": 90,
  "experience_relevance_score": 85,
  "format_score": 90
}}

Be critical and realistic in your assessment.
"""

        # Call the Google AI API requesting JSON
        result = call_google_ai_api(prompt, response_format="json")
        
        if isinstance(result, dict) and "overall_score" in result:
            return result["overall_score"]
        else:
            logger.error(f"Invalid response from ATS scoring: {result}")
            return calculate_fallback_ats_score(resume_text, job_description)
            
    except Exception as e:
        logger.error(f"Error calculating ATS score: {str(e)}")
        return calculate_fallback_ats_score(resume_text, job_description)

def calculate_fallback_ats_score(resume_text: str, job_description: str) -> float:
    """Fallback method for calculating ATS score"""
    # Count keyword matches
    job_words = set(job_description.lower().split())
    resume_words = set(resume_text.lower().split())
    matches = len(job_words.intersection(resume_words))
    
    # Calculate a basic score
    max_possible = len(job_words) * 0.6  # We don't expect 100% match
    raw_score = (matches / max_possible) * 100
    
    # Ensure score is between 50-95 for realism
    normalized_score = min(max(raw_score, 50), 95)
    return normalized_score

def generate_job_search_tips(resume_text: str, extracted_skills: List[str], job_title: str) -> Union[str, Dict[str, Any]]:
    """
    Generate personalized job search tips based on resume and skills.
    
    Args:
        resume_text: The text content of the resume
        extracted_skills: List of skills extracted from the resume
        job_title: The target job title
        
    Returns:
        A string containing job search tips
    """
    try:
        # Improved prompt structure based on the "Elements of a Good Prompt" guidance
        prompt = f"""###Context
I'm analyzing a resume from a candidate with skills in {', '.join(extracted_skills[:5])} who is seeking a {job_title} position.

###Resume Summary
{resume_text[:1000]}

###Instruction
Act as a personal career advisor with a calm, professional tone. Analyze the candidate's background and provide 5 highly personalized job search tips that will help this specific candidate stand out in their job search.

###Format
Present your response as 5 numbered, detailed tips in markdown format. Each tip should:
1. Begin with a bold header summarizing the advice
2. Include 2-3 sentences of specific, actionable guidance tailored to this candidate's background
3. Reference at least one specific skill or experience from the resume
4. End with a practical next step the candidate can take immediately

###Tone
Be encouraging but realistic. Use a professional, knowledgeable tone that builds confidence.

###Important
Your tips MUST be specific to this candidate's skills and experience - avoid generic advice that could apply to anyone.
Focus on networking strategies, application tactics, interview preparation, portfolio development, and industry-specific advice.
"""

        # Call the Google AI API
        response = call_google_ai_api(prompt)
        
        # If the response is a dictionary with an error, return the fallback
        if isinstance(response, dict) and "error" in response:
            return fallback_job_search_tips()
            
        return response
        
    except Exception as e:
        logger.error(f"Error generating job search tips: {str(e)}")
        return fallback_job_search_tips()

def fallback_job_search_tips() -> str:
    """Fallback job search tips when API is not available"""
    return """Job Search Tips:

1. Customize your resume for each application to highlight relevant skills
2. Build your professional network on LinkedIn and industry-specific platforms
3. Prepare for interviews by researching the company and practicing common questions
4. Follow up after applications and interviews with a personalized thank-you note
5. Consider freelance or project work to build experience in your target field"""

def generate_skill_questions(skill_name: str) -> Dict[str, Any]:
    """
    Generate challenging skill assessment questions for a specific skill.
    
    Args:
        skill_name: The name of the skill to generate questions for
        
    Returns:
        A dictionary containing skill assessment questions
    """
    try:
        prompt = f"""Create 5 challenging multiple-choice questions to test knowledge of {skill_name}.

For each question:
1. The question should test advanced knowledge, not basic concepts
2. Provide 4 answer options (A, B, C, D)
3. Indicate the correct answer
4. The questions should be diverse and cover different aspects of {skill_name}

Format each question as follows:
{{
  "question": "What is the output of the following Python code?\\n\\nx = [1, 2, 3]\\ny = x\\ny.append(4)\\nprint(x)",
  "options": ["[1, 2, 3]", "[1, 2, 3, 4]", "[4, 1, 2, 3]", "Error"],
  "answer": "[1, 2, 3, 4]"
}}

Return a JSON array containing 5 questions in this format.
"""

        # Call the Google AI API requesting JSON
        result = call_google_ai_api(prompt, response_format="json")
        
        if isinstance(result, list) and len(result) > 0:
            return result
        else:
            logger.error(f"Invalid response format for skill questions: {result}")
            return fallback_skill_questions(skill_name)
            
    except Exception as e:
        logger.error(f"Error generating skill questions for {skill_name}: {str(e)}")
        return fallback_skill_questions(skill_name)

def fallback_skill_questions(skill_name: str) -> List[Dict[str, Any]]:
    """Fallback skill questions when API is not available"""
    # Dictionary of predefined skill-specific questions
    skill_questions = {
        "python": [
            {
                "question": "What is the output of the following Python code?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)",
                "options": ["[1, 2, 3]", "[1, 2, 3, 4]", "[4, 1, 2, 3]", "Error"],
                "answer": "[1, 2, 3, 4]"
            },
            {
                "question": "Which of the following is NOT a built-in data type in Python?",
                "options": ["List", "Dictionary", "Array", "Tuple"],
                "answer": "Array"
            },
            {
                "question": "What is the time complexity of accessing an element in a Python dictionary?",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
                "answer": "O(1)"
            }
        ],
        # Additional skills omitted for brevity
    }
    
    # Convert skill name to lowercase for case-insensitive matching
    skill_lower = skill_name.lower()
    
    # Check if we have predefined questions for this skill
    for key in skill_questions:
        if key in skill_lower or skill_lower in key:
            return skill_questions[key]
    
    # If no matching skill found, return generic questions
    return [
        {
            "question": f"Which of the following is most closely associated with {skill_name}?",
            "options": ["Software Development", "Data Analysis", "Design", "Project Management"],
            "answer": "Software Development"  # Default
        },
        {
            "question": f"What is the best approach to improve your {skill_name} skills?",
            "options": [
                "Reading textbooks only", 
                "Watching video tutorials only", 
                "Hands-on practice with real projects", 
                "Memorizing technical terms"
            ],
            "answer": "Hands-on practice with real projects"
        },
        {
            "question": f"How important is {skill_name} in modern software development?",
            "options": ["Not important", "Somewhat important", "Very important", "Essential"],
            "answer": "Very important"
        }
    ]

def generate_cover_letter(resume_text: str, job_description: str, company_name: str) -> str:
    """
    Generate a personalized cover letter based on resume and job description.
    
    Args:
        resume_text: The text content of the resume
        job_description: The job description to target
        company_name: The name of the company
        
    Returns:
        A string containing the generated cover letter
    """
    try:
        prompt = f"""Generate a professional cover letter for a job application based on the provided resume and job description.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1000]}

COMPANY:
{company_name}

Create a compelling cover letter that:
1. Addresses the hiring manager professionally
2. Shows enthusiasm for the specific role at {company_name}
3. Highlights 3-4 relevant achievements or skills from the resume that match the job requirements
4. Demonstrates understanding of the company's industry and challenges
5. Includes a strong closing paragraph with a call to action
6. Is professional in tone, grammatically correct, and between 250-350 words

The cover letter should be personalized to this specific candidate, role, and company - avoid generic language.
"""

        # Call the Google AI API
        response = call_google_ai_api(prompt)
        
        # If the response is a dictionary with an error, return a fallback
        if isinstance(response, dict) and "error" in response:
            return f"Error generating cover letter: {response['error']}"
            
        return response
        
    except Exception as e:
        logger.error(f"Error generating cover letter: {str(e)}")
        return f"Error generating cover letter: {str(e)}"

def analyze_resume_strengths_weaknesses(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Analyze a resume's strengths and weaknesses compared to a job description.
    
    Args:
        resume_text: The text content of the resume
        job_description: The job description to compare against
        
    Returns:
        A dictionary containing strengths, weaknesses, and suggestions
    """
    try:
        prompt = f"""Perform a detailed analysis of this resume against the job description.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1000]}

Provide a comprehensive analysis with these sections:

1. STRENGTHS: List 3-5 specific strengths of this resume relative to the job requirements. For each strength, mention:
   - The specific skill or experience
   - Why it's valuable for this role
   - How it differentiates the candidate

2. WEAKNESSES: Identify 3-5 gaps or areas for improvement. For each weakness, note:
   - The specific skill or experience gap
   - Why it matters for this role
   - How significant this gap is (minor, moderate, critical)

3. SUGGESTIONS: Provide 3-5 specific, actionable recommendations to improve the resume. Each suggestion should:
   - Address a specific weakness
   - Include practical steps to implement
   - Explain how this would increase chances of getting hired

Format your response as a JSON object with these three keys (strengths, weaknesses, suggestions), each containing an array of detailed items.
"""

        # Call the Google AI API requesting JSON
        result = call_google_ai_api(prompt, response_format="json")
        
        if isinstance(result, dict) and "strengths" in result and "weaknesses" in result and "suggestions" in result:
            return result
        else:
            # Fallback
            return {
                "strengths": [
                    "Technical skills relevant to the position",
                    "Education background aligns with requirements",
                    "Previous experience in similar roles"
                ],
                "weaknesses": [
                    "Lack of quantifiable achievements",
                    "Missing specific keywords from job description",
                    "Limited demonstration of soft skills"
                ],
                "suggestions": [
                    "Add measurable achievements to experience points",
                    "Incorporate more keywords from the job description",
                    "Expand on relevant project experiences",
                    "Highlight soft skills through concrete examples",
                    "Tailor resume summary to directly address job requirements"
                ]
            }
            
    except Exception as e:
        logger.error(f"Error analyzing resume strengths/weaknesses: {str(e)}")
        # Fallback
        return {
            "strengths": [
                "Technical skills relevant to the position",
                "Education background aligns with requirements",
                "Previous experience in similar roles"
            ],
            "weaknesses": [
                "Lack of quantifiable achievements",
                "Missing specific keywords from job description",
                "Limited demonstration of soft skills"
            ],
            "suggestions": [
                "Add measurable achievements to experience points",
                "Incorporate more keywords from the job description",
                "Expand on relevant project experiences",
                "Highlight soft skills through concrete examples",
                "Tailor resume summary to directly address job requirements"
            ]
        }