"""Module to dynamically generate live job search platform URLs based on job title and location."""
import urllib.parse

def generate_job_platform_links(title: str, location: str) -> dict:
    """
    Generate search URLs for various external job platforms.
    
    Args:
        title (str): The job title to search for.
        location (str): The job location.
        
    Returns:
        dict: A dictionary mapping platform names to their respective search URLs.
    """
    if not title:
        title = ""
    if not location:
        location = ""
        
    encoded_title = urllib.parse.quote(title)
    encoded_location = urllib.parse.quote(location)
    
    # Naukri formatting (hyphens instead of spaces)
    naukri_title = title.replace(" ", "-").lower()
    naukri_location = location.replace(" ", "-").lower()
    
    links = {
        "indeed": f"https://in.indeed.com/jobs?q={encoded_title}&l={encoded_location}",
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={encoded_title}%20{encoded_location}",
        "naukri": f"https://www.naukri.com/{naukri_title}-jobs-in-{naukri_location}",
        "foundit": f"https://www.foundit.in/srp/results?query={encoded_title}&locations={encoded_location}",
        "wellfound": f"https://wellfound.com/jobs?search={encoded_title}",
        "glassdoor": f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={encoded_title}&locT=C&locName={encoded_location}"
    }
    
    # Conditionally add Internshala if the role is an internship
    if "intern" in title.lower() or "internship" in title.lower():
        links["internshala"] = f"https://internshala.com/internships/{naukri_title}-internship-in-{naukri_location}/"
        
    return links
