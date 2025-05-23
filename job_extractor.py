import csv
import os
import pandas as pd
from datetime import datetime

def save_job_to_csv(job_data, search_query):
    """Save job data to CSV file"""
    if not job_data:
        print("No job data to save")
        return
    
    # Create filename based on search query
    filename = f"{search_query.replace(' ', '_').lower()}_jobs.csv"
    
    # Define CSV headers
    fieldnames = [
        'job_title', 'company', 'posted', 'location', 'salary', 
        'work_type', 'employment_type', 'hiring_cafe_url', 
        'external_url', 'search_query', 'extracted_date', 'job_description'
    ]
    
    # Check if file exists
    file_exists = os.path.isfile(filename)
    
    # Write to CSV
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
            print(f"Created new CSV file: {filename}")
        else:
            print(f"Appending to existing CSV file: {filename}")
        
        # Write job data
        writer.writerow(job_data)
        print(f"Saved job to {filename}")

def parse_job_details(job_details_list):
    """Parse job details list and categorize them"""
    salary = ""
    work_type = ""
    employment_type = ""
    
    for detail in job_details_list:
        detail = detail.strip()
        if "$" in detail or "k" in detail:
            salary = detail
        elif detail.lower() in ['remote', 'hybrid', 'onsite', 'in-office']:
            work_type = detail
        elif detail.lower() in ['full time', 'part time', 'contract', 'freelance']:
            employment_type = detail
    
    return salary, work_type, employment_type

def check_job_already_scraped_by_url(external_url, search_query):
    """Check if a job has already been scraped by comparing external URLs"""
    filename = f"{search_query.replace(' ', '_').lower()}_jobs.csv"
    
    # If file doesn't exist, job hasn't been scraped
    if not os.path.isfile(filename):
        return False
    
    if not external_url or external_url == "Not found":
        return False
    
    try:
        # Read the existing CSV file
        df = pd.read_csv(filename)
        
        # Check if this external URL already exists
        existing_urls = df['external_url'].astype(str).str.strip()
        external_url_clean = str(external_url).strip()
        
        if external_url_clean in existing_urls.values:
            print(f"Found duplicate job by URL: {external_url_clean}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error checking existing jobs by URL: {e}")
        return False

def check_job_already_scraped(job_title, company, location, search_query):
    """Check if a job has already been scraped by looking in the CSV file"""
    filename = f"{search_query.replace(' ', '_').lower()}_jobs.csv"
    
    # If file doesn't exist, job hasn't been scraped
    if not os.path.isfile(filename):
        return False
    
    try:
        # Read the existing CSV file
        df = pd.read_csv(filename)
        
        # Clean up the data for comparison
        job_title_clean = job_title.strip().lower() if job_title else ""
        company_clean = company.strip().lower().replace('@', '').strip() if company else ""
        location_clean = location.strip().lower() if location else ""
        
        # Look for matches with some flexibility
        for _, row in df.iterrows():
            existing_title = str(row.get('job_title', '')).strip().lower()
            existing_company = str(row.get('company', '')).strip().lower().replace('@', '').strip()
            existing_location = str(row.get('location', '')).strip().lower()
            
            # Check for title and company match (location might be different between preview and detail)
            title_match = existing_title == job_title_clean or (job_title_clean and job_title_clean in existing_title)
            company_match = existing_company == company_clean or (company_clean and company_clean in existing_company)
            
            # If we have good title and company matches, consider it a duplicate
            if title_match and company_match and job_title_clean and company_clean:
                print(f"Found duplicate: '{job_title_clean}' at '{company_clean}' matches existing '{existing_title}' at '{existing_company}'")
                return True
        
        return False
        
    except Exception as e:
        print(f"Error checking existing jobs: {e}")
        return False

def extract_job_preview_info(element):
    """Extract job info from the grid element preview to check for duplicates"""
    try:
        job_title = ""
        company = ""
        location = ""
        
        # Extract job title - look for the title span in the card
        try:
            title_candidates = [
                "span.w-full.font-bold.text-start.line-clamp-3",
                "span.font-bold.text-start.line-clamp-3", 
                "div.mt-1 span",
                ".font-bold"
            ]
            for selector in title_candidates:
                title_elements = element.locator(selector)
                if title_elements.count() > 0:
                    job_title = title_elements.first.text_content().strip()
                    if job_title:
                        break
        except Exception as e:
            print(f"Error extracting title: {e}")
        
        # Extract location - look for location span with SVG
        try:
            location_candidates = [
                "div:has(svg) span.line-clamp-2",
                "div.flex.items-center span",
                ".line-clamp-2"
            ]
            for selector in location_candidates:
                location_elements = element.locator(selector)
                if location_elements.count() > 0:
                    for i in range(location_elements.count()):
                        loc_text = location_elements.nth(i).text_content().strip()
                        # Skip if it's the job title or other non-location text
                        if loc_text and "," in loc_text and "United States" in loc_text:
                            location = loc_text
                            break
                    if location:
                        break
        except Exception as e:
            print(f"Error extracting location: {e}")
        
        # Extract company from the description
        try:
            company_candidates = [
                "span.font-light span.font-bold",
                "span:has-text(':')",
                ".font-bold"
            ]
            for selector in company_candidates:
                company_elements = element.locator(selector)
                if company_elements.count() > 0:
                    for i in range(company_elements.count()):
                        comp_text = company_elements.nth(i).text_content().strip()
                        if comp_text and ":" in comp_text:
                            company = comp_text.replace(':', '').strip()
                            break
                    if company:
                        break
        except Exception as e:
            print(f"Error extracting company: {e}")
        
        print(f"Debug - Extracted: Title='{job_title}', Company='{company}', Location='{location}'")
        return job_title, company, location
        
    except Exception as e:
        print(f"Error extracting preview info: {e}")
        try:
            print(f"Element HTML sample: {element.inner_html()[:500]}...")
        except:
            print("Could not get element HTML")
        return "", "", ""