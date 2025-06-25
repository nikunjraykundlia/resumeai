"""
Optimized OpenAI API helper module for resume analysis
"""
import os
import json
import logging

# Setup OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GPT_MODEL = "gpt-4o"  # Latest model as of May 2024
OPENAI_AVAILABLE = False

try:
    from openai import OpenAI
    if OPENAI_API_KEY:
        openai = OpenAI(api_key=OPENAI_API_KEY)
        OPENAI_AVAILABLE = True
        logging.info("OpenAI API initialized")
    else:
        logging.warning("OpenAI API key not found")
except Exception as e:
    logging.error(f"OpenAI init error: {e}")

# Common reusable utility functions
def call_openai_api(prompt, system_role="You are a helpful AI assistant", max_tokens=800, json_format=False, retry_count=1):
    """Centralized API calling function with proper error handling and rate limit management"""
    if not OPENAI_AVAILABLE:
        logging.warning("OpenAI API not available, using fallback functionality")
        return None
        
    try:
        params = {
            "model": GPT_MODEL,
            "messages": [
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens
        }
        
        if json_format:
            params["response_format"] = {"type": "json_object"}
            
        response = openai.chat.completions.create(**params)
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e).lower()
        if retry_count > 0 and ("rate limit" in error_msg or "quota" in error_msg or "429" in error_msg):
            # Wait briefly and retry once for rate limit errors
            import time
            logging.warning(f"OpenAI API rate limit hit, retrying after delay... ({retry_count} attempts left)")
            time.sleep(2)  # Short delay before retry
            return call_openai_api(prompt, system_role, max_tokens, json_format, retry_count - 1)
        
        logging.error(f"OpenAI API error: {e}")
        return None

def get_resume_prompt(resume_text, job_description=None, extra_context=None, max_resume_chars=2000, max_job_chars=1000):
    """Standardized prompt builder for resume-related queries"""
    prompt = ""
    
    if resume_text:
        prompt += f"RESUME:\n{resume_text[:max_resume_chars]}\n\n"
        
    if job_description:
        prompt += f"JOB DESCRIPTION:\n{job_description[:max_job_chars]}\n\n"
        
    if extra_context:
        prompt += f"{extra_context}\n\n"
        
    return prompt.strip()

# Main feature functions
def generate_improvement_suggestions(resume_text, job_description, extracted_skills):
    """Generate personalized improvement suggestions for a resume"""
    if not OPENAI_AVAILABLE:
        return fallback_improvement_suggestions()
    
    prompt = get_resume_prompt(
        resume_text, 
        job_description,
        f"SKILLS: {', '.join(extracted_skills[:20])}\n\nProvide 5 specific suggestions to improve this resume for the job. Focus on content gaps, skills presentation, achievements, formatting, and keywords. Format with clear headings and bullet points."
    )
    
    result = call_openai_api(
        prompt=prompt,
        system_role="You are an expert resume coach specializing in resume improvement.",
        max_tokens=800
    )
    
    return result or fallback_improvement_suggestions()

def generate_job_search_tips(resume_text, extracted_skills, job_title):
    """Generate personalized job search tips"""
    if not OPENAI_AVAILABLE:
        return fallback_job_search_tips()
    
    prompt = get_resume_prompt(
        resume_text, 
        extra_context=f"SKILLS: {', '.join(extracted_skills[:20])}\nTARGET POSITION: {job_title}\n\nProvide 5-7 specific job search tips tailored to this person's background for a {job_title} position. Include application strategies, networking, skills to highlight, and interview preparation. Use headings and bullet points."
    )
    
    result = call_openai_api(
        prompt=prompt,
        system_role="You are a career coach specializing in job search strategies.",
        max_tokens=700
    )
    
    return result or fallback_job_search_tips()

def analyze_resume_strengths_weaknesses(resume_text, job_description):
    """Analyze resume strengths and weaknesses against a job description"""
    if not OPENAI_AVAILABLE:
        logging.warning("OpenAI not available for resume analysis, using fallback")
        return fallback_resume_analysis()
    
    prompt = get_resume_prompt(
        resume_text, 
        job_description,
        "Analyze this resume against the job description and provide:\n1. 3-5 specific strengths\n2. 3-5 specific weaknesses\n3. 5 actionable improvement suggestions\n\nFormat as JSON with keys: 'strengths', 'weaknesses', 'suggestions', each containing arrays of strings."
    )
    
    # Try with retry logic for rate limits
    for attempt in range(2):  # Try twice
        try:
            result = call_openai_api(
                prompt=prompt,
                system_role="You are an expert resume analyst providing detailed feedback.",
                max_tokens=800,
                json_format=True,
                retry_count=1  # Already has built-in retry
            )
            
            if result:
                try:
                    parsed = json.loads(result)
                    if all(k in parsed for k in ["strengths", "weaknesses", "suggestions"]):
                        return parsed
                except json.JSONDecodeError as json_err:
                    logging.error(f"JSON parse error in resume analysis: {json_err}")
            
            # If we reach here on the first attempt, we got a result but it wasn't parseable
            if attempt == 0:
                logging.warning("First analysis attempt failed, retrying with simplified prompt")
                # Simplify the prompt for the second attempt
                prompt = get_resume_prompt(
                    resume_text, 
                    job_description,
                    "Analyze this resume and provide 3 strengths, 3 weaknesses, and 3 suggestions in JSON format with keys: 'strengths', 'weaknesses', 'suggestions'."
                )
            else:
                # Second attempt failed too
                logging.error("Both analysis attempts failed, using fallback")
                
        except Exception as e:
            logging.error(f"Error in resume analysis attempt {attempt+1}: {str(e)}")
            if attempt == 1:  # Last attempt
                break
    
    return fallback_resume_analysis()

def generate_cover_letter(resume_text, job_description, company_name):
    """Generate a personalized cover letter"""
    if not OPENAI_AVAILABLE:
        return fallback_cover_letter(company_name)
    
    prompt = get_resume_prompt(
        resume_text, 
        job_description,
        f"COMPANY: {company_name}\n\nCreate a professional, concise cover letter (250-350 words) with:\n- Professional greeting\n- 3-4 paragraphs highlighting relevant achievements\n- Strong closing with call to action\n- Professional sign-off\n\nMake it specific to this company and role, avoid generic phrases like 'I believe I would be a good fit'."
    )
    
    result = call_openai_api(
        prompt=prompt,
        system_role="You are an expert cover letter writer highlighting candidate strengths.",
        max_tokens=1000
    )
    
    return result or fallback_cover_letter(company_name)

def create_resume_chatbot_response(resume_text, user_query):
    """Generate AI chatbot responses about resume questions"""
    if not OPENAI_AVAILABLE:
        return fallback_chatbot_response(user_query)
    
    prompt = f"RESUME:\n{resume_text[:2000]}\n\nQUESTION: {user_query}\n\nProvide a specific, helpful response that directly addresses the question with relevant details from the resume. Be conversational but professional."
    
    result = call_openai_api(
        prompt=prompt,
        system_role="You are a helpful resume advisor providing specific feedback.",
        max_tokens=600
    )
    
    return result or fallback_chatbot_response(user_query)

def generate_skill_questions(skill_name):
    """Generate skill assessment questions for a specific skill"""
    if not OPENAI_AVAILABLE:
        return fallback_skill_questions(skill_name)
        
    prompt = f"Create 3-5 challenging multiple-choice questions to test knowledge of {skill_name}. Each question should have 4 options and one correct answer. Format as JSON array with 'question', 'options', and 'answer' keys."
    
    result = call_openai_api(
        prompt=prompt,
        system_role=f"You are an expert in {skill_name} creating assessment questions.",
        max_tokens=800,
        json_format=True
    )
    
    try:
        if result:
            return json.loads(result)
    except:
        pass
        
    return fallback_skill_questions(skill_name)

# Fallback functions
def fallback_improvement_suggestions():
    return """# Resume Improvement Suggestions

## Content Alignment
- Review job description and incorporate key terms and requirements
- Tailor your summary to directly address the specific role

## Skills Enhancement
- Organize skills into clear categories (technical, soft, domain)
- Add specific versions/experience levels with technical skills

## Achievement Focus
- Replace general duties with specific, measurable achievements
- Add metrics and percentages to quantify your impact

## Resume Structure
- Ensure most relevant experience appears at the top
- Use consistent formatting throughout

## ATS Optimization
- Incorporate more exact keywords from the job posting
- Use standard section headings that ATS systems easily parse"""

def fallback_job_search_tips():
    return """# Job Search Tips

## Application Strategy
- Customize your resume for each application to highlight relevant skills
- Use industry-specific keywords from the job description

## Networking
- Build your professional network on LinkedIn and industry platforms
- Attend virtual and in-person industry events

## Interview Preparation
- Research the company thoroughly before interviews
- Prepare specific examples that demonstrate your skills

## Follow-Up Strategy
- Send a personalized thank-you email within 24 hours after interviews
- Reference specific discussion points from the interview"""

def fallback_resume_analysis():
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

def fallback_cover_letter(company_name):
    return f"""Dear Hiring Manager,

I am writing to express my interest in joining {company_name}. With my background and skills, I believe I can make valuable contributions to your organization.

Through my professional experience, I have developed strong skills in problem-solving, communication, and technical expertise relevant to this position. I am particularly drawn to {company_name}'s innovative approach.

I welcome the opportunity to discuss how my qualifications align with your needs. Thank you for considering my application.

Sincerely,
[Your Name]"""

def fallback_chatbot_response(user_query):
    """Provide diverse fallback responses based on query keywords"""
    query_lower = user_query.lower()
    
    # Greeting or introduction responses
    if any(word in query_lower for word in ['hi', 'hello', 'hey', 'who', 'what are you', 'name']):
        return f"""Hello! I'm ResumeAI's assistant, designed to help with resume and career questions.
        
I'd be happy to analyze your resume and provide personalized job recommendations. 
Our system can evaluate your skills, experience, and qualifications to match you with suitable positions.

How can I help with your resume or job search today?"""

    # Resume improvement questions
    elif any(word in query_lower for word in ['improve', 'better', 'enhance', 'fix', 'update']):
        return f"""To improve your resume, consider these proven strategies:

1. Start with a strong professional summary highlighting your unique value
2. Quantify your achievements with specific metrics and results
3. Tailor your skills section to match job descriptions
4. Use action verbs (achieved, implemented, led) instead of passive language
5. Include industry-specific keywords to pass ATS screening
6. Maintain consistent formatting and a clean, professional layout

Would you like more specific advice on a particular section of your resume?"""

    # Job search or interview questions
    elif any(word in query_lower for word in ['job', 'interview', 'career', 'hire', 'company']):
        return f"""For successful job applications and interviews:

1. Research target companies thoroughly before applying
2. Customize each application to highlight relevant experience
3. Prepare concrete examples of past achievements using the STAR method
4. Practice answers to common interview questions in your field
5. Develop a strong personal brand across LinkedIn and professional platforms
6. Follow up after interviews with a personalized thank-you note

What specific part of the job search process can I help with?"""

    # Skills assessment questions
    elif any(word in query_lower for word in ['skill', 'ability', 'qualification', 'test', 'assessment']):
        return f"""To showcase and develop your professional skills effectively:

1. Create a clear skills section organized by category (technical, soft, industry-specific)
2. Back up skill claims with specific examples from your experience
3. Consider pursuing relevant certifications in your field
4. Identify skill gaps by comparing your profile to job requirements
5. Use projects and volunteer work to demonstrate practical application
6. Continuously update your skills through courses and industry engagement

What specific skills are you looking to highlight or develop?"""

    # Default response for other queries
    else:
        return f"""Thank you for your question about: "{user_query}"

I can provide guidance on:
• Resume optimization and improvement
• Job searching strategies and application techniques
• Skills assessment and development
• Career planning and advancement
• Interview preparation
• Industry-specific advice

Please try asking a more specific question related to these areas for better assistance."""

def fallback_skill_questions(skill_name):
    # Provide basic generic questions when needed
    return [
        {
            "question": f"What is a key best practice when working with {skill_name}?",
            "options": [
                "Always work independently", 
                "Document your work thoroughly", 
                "Avoid testing until completion", 
                "Use outdated techniques"
            ],
            "answer": "Document your work thoroughly"
        },
        {
            "question": f"Which skill complements {skill_name} best?",
            "options": [
                "Project management", 
                "Communication", 
                "Artistic ability", 
                "Physical fitness"
            ],
            "answer": "Communication"
        }
    ]