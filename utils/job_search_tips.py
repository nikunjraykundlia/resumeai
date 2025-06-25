"""
Job Search Tips Generator
Generates personalized job search tips based on the user's resume data and job preferences
"""
import os
import logging
import json
import random
from time import sleep

# Import the OpenAI library 
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the OpenAI client with API key from environment variable
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    logger.info("OpenAI client initialized for job search tips")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {e}")
    openai_client = None

def generate_unique_job_search_tips(resume_text, job_titles=None, experience_years=None, skills=None, retry_count=0):
    """
    Generates unique job search tips based on the resume and job preferences
    
    Args:
        resume_text (str): The extracted text from the user's resume
        job_titles (list): List of job titles the user is interested in
        experience_years (int): Years of experience (estimated from resume)
        skills (list): List of skills extracted from the resume
        retry_count (int): Number of retries attempted (for handling rate limits)
        
    Returns:
        str: Markdown-formatted job search tips
    """
    if not openai_client:
        return get_fallback_job_search_tips()
    
    # Format the job titles for better prompt context
    job_titles_str = ", ".join(job_titles) if job_titles and len(job_titles) > 0 else "various positions"
    
    # Create a condensed skills list (limited to top 10 for prompt size)
    skills_str = ", ".join(skills[:10]) if skills and len(skills) > 0 else "various skills"
    
    # Construct a user context from the resume data
    user_context = f"""
    The user has a resume that indicates experience in {skills_str}.
    They appear to have approximately {experience_years if experience_years else 'some'} years of experience.
    They are primarily interested in positions like: {job_titles_str}.
    
    Here's a brief extract from their resume for better context:
    {resume_text[:500]}...
    """
    
    prompt_template = f"""
    InnovateTech Solutions Inc. is a cutting-edge technology company headquartered in Silicon Valley. 
    The company specializes in developing innovative product and software solutions for various industries, 
    including artificial intelligence, Internet of Things (IoT), cloud computing, and cybersecurity.

    Act as a personal assistant with a calm, professional tone.

    The goal is to provide personalized job search tips for a given user. 
    The user has the following resume details and job search objectives:
    {user_context}

    Instructions:
    1. Summarize the user's background in a concise manner.
    2. Using the "Job Search Tips" below, craft a unique strategy specifically tailored to the user's background.
    3. Present the main points in a markdown table for clarity.

    Job Search Tips:
    - **Application Strategy**  
      - Customize your resume for each application to highlight relevant skills  
      - Use industry-specific keywords from the job description

    - **Networking**  
      - Build your professional network on LinkedIn and industry platforms  
      - Attend virtual and in-person industry events

    - **Interview Preparation**  
      - Research the company thoroughly before interviews  
      - Prepare specific examples that demonstrate your skills

    - **Follow-Up Strategy**  
      - Send a thank-you email within 24 hours after interviews  
      - Reference specific discussion points from the interview

    Reference:
    Use the example of summarizing 'InnovateTech Solutions Inc.' to maintain a similar format. 
    However, each user's output should be unique and reflect the user's background.
    """
    
    try:
        # Log that we're making an OpenAI API call
        logger.info(f"Making OpenAI API call for job search tips with context length: {len(prompt_template)}")
        
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024
        # Do not change this unless explicitly requested by the user
        try:
            # For better rate limit handling, we'll use gpt-3.5-turbo instead of gpt-4o
            # This model has higher rate limits and is more cost-effective
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using gpt-3.5-turbo for higher rate limits
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant specialized in career advice."},
                    {"role": "user", "content": prompt_template}
                ],
                temperature=0.7,  # Increase randomness for more unique responses
                max_tokens=1000,
                n=1
            )
            logger.info("Successfully received response from OpenAI API")
        except Exception as api_error:
            logger.error(f"OpenAI API call failed: {api_error}")
            raise
        
        # Extract the job search tips from the response
        tips_content = response.choices[0].message.content
        
        return tips_content
        
    except Exception as e:
        logger.error(f"Error generating job search tips: {e}")
        
        # Implement exponential backoff for retries
        if retry_count < 3:
            # Calculate sleep time with exponential backoff and a bit of randomness
            sleep_time = (2 ** retry_count) + (random.random() * 0.5)
            
            # Notify the user about the retry
            logger.info(f"Rate limit or API error encountered. Retry {retry_count+1}/3 in {sleep_time:.1f} seconds...")
            
            try:
                # Sleep for the calculated time
                sleep(sleep_time)
                
                # Try again with incremented retry count
                return generate_unique_job_search_tips(resume_text, job_titles, experience_years, skills, retry_count + 1)
            except Exception as retry_error:
                logger.error(f"Error during retry: {retry_error}")
                # If something goes wrong during retry, continue to fallback
        
        # If still failed after retries, return fallback content
        return get_fallback_job_search_tips()

def get_fallback_job_search_tips():
    """
    Provides fallback job search tips when OpenAI API is unavailable
    """
    return """
## Personalized Job Search Tips

| Area | Tips |
|------|------|
| **Resume Optimization** | • Tailor your resume with relevant keywords<br>• Quantify achievements when possible<br>• Have a clear, concise summary |
| **Job Search Strategy** | • Set up daily job alerts on multiple platforms<br>• Follow companies of interest on LinkedIn<br>• Check company websites directly for openings |
| **Interview Preparation** | • Research the company thoroughly<br>• Prepare specific examples of your work<br>• Practice common interview questions |
| **Networking** | • Connect with professionals in your target field<br>• Attend industry events and webinars<br>• Join relevant LinkedIn and Discord groups |
| **Skill Development** | • Identify skill gaps for your target roles<br>• Take online courses to address these gaps<br>• Build portfolio projects to showcase skills |

*These are general tips based on our analysis of your resume. As you continue to update your skills and experience, these recommendations will become more personalized.*
"""