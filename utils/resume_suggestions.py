"""
Resume Suggestions Generator
Generates personalized resume improvement suggestions based on resume analysis
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
    logger.info("OpenAI client initialized for resume suggestions")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {e}")
    openai_client = None

def generate_resume_suggestions(resume_text, skills=None, job_title=None, retry_count=0):
    """
    Generates personalized resume improvement suggestions based on resume content
    
    Args:
        resume_text (str): The extracted text from the user's resume
        skills (list): List of skills extracted from the resume
        job_title (str): Target job title or role
        retry_count (int): Number of retries attempted (for handling rate limits)
        
    Returns:
        str: Markdown-formatted resume improvement suggestions
    """
    if not openai_client:
        return get_fallback_resume_suggestions()
    
    # Format the skills for better prompt context
    skills_str = ", ".join(skills[:10]) if skills and len(skills) > 0 else "various skills"
    
    # Create a prompt that will generate personalized resume suggestions
    prompt_template = f"""
    You are a professional resume reviewer and career expert.
    
    I need you to review the following resume and provide specific, actionable improvement suggestions.
    
    Resume Text:
    {resume_text[:1000]}...
    
    Skills Identified: {skills_str}
    
    Target Job: {job_title if job_title else "Various tech positions"}
    
    Please provide resume improvement suggestions in the following areas:
    
    1. Content Optimization - What specific content should be added, removed, or modified
    2. Formatting & Structure - How to improve the visual layout and organization
    3. ATS Optimization - How to make the resume more ATS-friendly
    4. Impact Statements - How to better quantify and showcase achievements
    5. Skills Presentation - How to better highlight relevant skills
    
    Format your response in Markdown, with each section having a clear heading and 2-3 specific, actionable bullet points.
    Keep your suggestions concise, practical, and tailored to this specific resume.
    """
    
    try:
        # Log that we're making an OpenAI API call
        logger.info(f"Making OpenAI API call for resume suggestions with context length: {len(prompt_template)}")
        
        try:
            # For better rate limit handling, we'll use gpt-3.5-turbo
            # This model has higher rate limits and is more cost-effective
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using gpt-3.5-turbo for higher rate limits
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer and career coach."},
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
        
        # Extract the resume suggestions from the response
        suggestions_content = response.choices[0].message.content
        
        return suggestions_content
        
    except Exception as e:
        logger.error(f"Error generating resume suggestions: {e}")
        
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
                return generate_resume_suggestions(resume_text, skills, job_title, retry_count + 1)
            except Exception as retry_error:
                logger.error(f"Error during retry: {retry_error}")
                # If something goes wrong during retry, continue to fallback
        
        # If still failed after retries, return fallback content
        return get_fallback_resume_suggestions()

def get_fallback_resume_suggestions():
    """
    Provides fallback resume improvement suggestions when OpenAI API is unavailable
    """
    return """
## Resume Improvement Suggestions

### Content Optimization
- **Quantify Achievements**: Add specific metrics and results to demonstrate impact (e.g., "Increased sales by 20%" rather than "Increased sales")
- **Use Action Verbs**: Begin bullet points with strong action verbs like "Developed," "Implemented," or "Coordinated"
- **Tailor Content**: Customize your resume for each application by emphasizing relevant experiences

### ATS Optimization
- **Include Keywords**: Incorporate industry-specific terms and skills from the job description
- **Use Standard Section Headings**: Stick with conventional headings like "Experience," "Skills," and "Education"
- **Avoid Complex Formatting**: Remove tables, graphics, and unusual fonts that ATS systems struggle to parse

### Skills Presentation
- **Organize by Relevance**: List most relevant skills first based on the job description
- **Include Proficiency Levels**: Consider adding expertise levels (e.g., "Proficient in Python, Familiar with Java")
- **Balance Technical & Soft Skills**: Include both technical capabilities and transferable skills like communication

### Formatting & Structure
- **Consistent Styling**: Maintain uniform formatting for dates, company names, and section headers
- **Strategic White Space**: Use adequate spacing between sections for improved readability
- **One-Page Rule**: For most positions, keep your resume to a single page unless you have 10+ years of experience

### Impact Statements
- **Use the STAR Method**: Structure achievements as Situation, Task, Action, and Result
- **Focus on Outcomes**: Emphasize results rather than responsibilities
- **Show Problem-Solving**: Highlight how you overcame challenges or improved processes
"""