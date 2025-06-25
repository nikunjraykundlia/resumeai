"""Adzuna API helper with caching and proper credential handling."""
import os
import logging
import re
import requests
from functools import lru_cache
from urllib.parse import quote

# ---------------------------------------------------------------------------
# Load credentials from environment variables (expect .env loaded elsewhere)
# ---------------------------------------------------------------------------
APP_ID = os.getenv("ADZUNA_APP_ID")
API_KEY = os.getenv("ADZUNA_API_KEY")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=128)
def search_jobs(keywords: str,
                location: str = "Remote",
                page: int = 1,
                results_per_page: int = 5):
    """Query Adzuna Jobs API.

    Args:
        keywords: Job title / keywords.
        location: Where parameter; "Remote" = omit from query.
        page: Page index (1-based per Adzuna spec).
        results_per_page: 1-50 allowed.

    Returns:
        List[dict]: formatted job dictionaries. Empty list on error or no creds.
    """
    # Guard: credentials present
    if not APP_ID or not API_KEY:
        logger.error("Adzuna credentials missing – set ADZUNA_APP_ID and ADZUNA_API_KEY in .env")
        return []

    # Basic sanitise
    keywords = (keywords or "").strip() or "developer"
    formatted_keywords = quote(keywords)

    base_url = "https://api.adzuna.com/v1/api/jobs"
    country = "gb"  # default to UK; could make param later
    url = f"{base_url}/{country}/search/{page}"

    params = {
        "app_id": APP_ID,
        "app_key": API_KEY,
        "results_per_page": results_per_page,
        "what": formatted_keywords,
        "content-type": "application/json",
    }
    if location.lower() not in {"remote", "any"}:
        params["where"] = location

    try:
        response = requests.get(url, params=params, timeout=6)
    except requests.RequestException as exc:
        logger.error("Adzuna request failed: %s", exc)
        return []

    if response.status_code != 200:
        logger.error("Adzuna error %s – %s", response.status_code, response.text[:200])
        return []

    data = response.json()
    jobs = data.get("results", [])

    formatted = []
    for job in jobs:
        desc = re.sub(r"<[^>]+>", "", job.get("description", ""))
        if len(desc) > 400:
            desc = desc[:400] + "…"

        formatted.append({
            "title": job.get("title", "Unknown Title"),
            "company": job.get("company", {}).get("display_name", "Unknown Company"),
            "description": desc,
            "match_score": 70 + (hash(job.get("id", "")) % 25),
            "apply_url": job.get("redirect_url", "#"),
            "location": job.get("location", {}).get("display_name", location),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "created": job.get("created"),
        })

    return formatted


@lru_cache(maxsize=128)
def search_jobs(keywords, location="Remote", page=1, results_per_page=5):
    """
    Search for jobs using the Adzuna API
    
    Args:
        keywords (str): Job title or keywords to search for
        location (str): Location to search in, default is "Remote"
        page (int): Page number for results
        results_per_page (int): Number of results per page
        
    Returns:
        list: List of job dictionaries or empty list if error
    """
    if not APP_ID or not API_KEY:
        logging.error("Adzuna credentials missing: ensure ADZUNA_APP_ID and ADZUNA_API_KEY are set in your .env")
        return []

    try:
                # Prepare the URL
        base_url = "https://api.adzuna.com/v1/api/jobs"
        country = "gb"  # Default to UK
        
        # Format keywords for URL
        formatted_keywords = quote(keywords)
        
        # Build the URL
        url = f"{base_url}/{country}/search/{page}"
        
        # Set up parameters
        params = {
            "app_id": APP_ID,
            "app_key": API_KEY,
            "results_per_page": results_per_page,
            "what": formatted_keywords,
            "content-type": "application/json"
        }
        
        # Add location parameter if not "Remote"
        if location.lower() != "remote":
            params["where"] = location
        
        # Make the request
        response = requests.get(url, params=params, timeout=6)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            
            # Format the results
            formatted_jobs = []
            for job in data.get("results", []):
                # Calculate match score - simple random value between 75-95 for demonstration
                match_score = hash(job.get("id", "")) % 20 + 75
                
                formatted_job = {
                    "title": job.get("title", "Unknown Title"),
                    "company": job.get("company", {}).get("display_name", "Unknown Company"),
                    "description": job.get("description", "No description available"),
                    "match_score": match_score,
                    "apply_url": job.get("redirect_url", "#"),
                    "location": job.get("location", {}).get("display_name", "Unknown Location"),
                    "salary_min": job.get("salary_min", "Not specified"),
                    "salary_max": job.get("salary_max", "Not specified"),
                    "created": job.get("created", "Unknown")
                }
                formatted_jobs.append(formatted_job)
            
            return formatted_jobs
        else:
            logging.error(f"Error fetching jobs: {response.status_code} {response.text}")
            return []
        
    except Exception as e:
        logging.error(f"Exception in Adzuna API call: {str(e)}")
        return []

def calculate_job_match_score(resume_text, job_description):
    """
    Calculate a match score between a resume and job description
    
    Args:
        resume_text (str): The resume text content
        job_description (str): The job description text
        
    Returns:
        int: Match score between 0-100
    """
    # Convert to lowercase for case-insensitive matching
    resume_lower = resume_text.lower()
    job_lower = job_description.lower()
    
    # Split into words and create sets for comparison
    resume_words = set(resume_lower.split())
    job_words = set(job_lower.split())
    
    # Calculate common words
    common_words = resume_words.intersection(job_words)
    
    # Calculate score based on percentage of job keywords found in resume
    # Weighting towards finding job keywords in the resume
    if len(job_words) > 0:
        score = (len(common_words) / len(job_words)) * 100
    else:
        score = 50  # Default middle score
    
    # Ensure score is between 0-100
    score = min(max(score, 0), 100)
    
    # Adjust to make more realistic (between 65-95)
    adjusted_score = 65 + (score * 0.3)
    
    return int(adjusted_score)

def get_fallback_jobs():
    """Return fallback job listings when API fails"""
    return [
        {
            "title": "Software Developer",
            "company": "Example Tech",
            "description": "We're looking for a software developer with strong skills in web development.",
            "match_score": 85,
            "apply_url": "https://example.com/jobs/software-developer",
            "location": "Remote",
            "salary_min": 70000,
            "salary_max": 90000,
            "created": "2025-04-01"
        },
        {
            "title": "Data Scientist",
            "company": "Data Analytics Inc",
            "description": "Seeking an experienced data scientist with machine learning expertise.",
            "match_score": 78,
            "apply_url": "https://example.com/jobs/data-scientist",
            "location": "New York",
            "salary_min": 85000,
            "salary_max": 110000,
            "created": "2025-04-02"
        }
    ]