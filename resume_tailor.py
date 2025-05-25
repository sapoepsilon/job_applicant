#!/usr/bin/env python3
"""
Resume Tailoring Script

This script reads job data from a CSV file, analyzes job descriptions using Gemini AI,
and creates tailored resumes in Markdown format, then converts them to PDF.

Usage:
    python resume_tailor.py --csv-path /path/to/jobs.csv
"""

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from google import genai
from google.genai import types
from dotenv import load_dotenv
import json
import re
from datetime import datetime
import time
from markdown_to_pdf import MarkdownToPDFConverter

# Load environment variables
load_dotenv()

class ResumeTailor:
    def __init__(self, 
                 resumes_dir: str = "/Users/ismatullamansurov/Documents/Latex Resumes"):
        """Initialize the Resume Tailor with Gemini AI and resume directory."""
        self.resumes_dir = Path(resumes_dir)
        self.output_dir = Path("tailored_resumes")
        self.markdown_output_dir = Path("tailored_resumes_markdown")
        self.pdf_output_dir = Path("tailored_resumes_pdf")
        
        self.markdown_output_dir.mkdir(exist_ok=True)
        self.pdf_output_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.5-flash-preview-05-20'
        # self.model = 'gemini-2.5-pro-preview-05-06'
        self.last_error = None  # Track last error for reporting
        
        # Read config.py for personal info
        self.config = self._read_config()
        
        # Initialize markdown to PDF converter
        self.pdf_converter = MarkdownToPDFConverter()
    
    def _read_config(self) -> Dict[str, str]:
        """Read personal information from config.py."""
        try:
            from config import PERSONAL_INFO
            return PERSONAL_INFO
        except ImportError:
            print("Warning: config.py not found. Using default personal info.")
            return {
                'name': 'John Doe',
                'email': 'john@doe.dev',
                'phone': '',
                'website': 'doe.dev',
                'github': 'github.com/johndoe',
                'linkedin': ''
            }
        
    def read_csv(self, csv_path: str) -> List[Dict[str, Any]]:
        """Read job data from CSV file."""
        jobs = []
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    jobs.append(row)
            print(f"Successfully read {len(jobs)} jobs from {csv_path}")
            return jobs
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []
    
    def update_csv_resume_status(self, csv_path: str, job_data: Dict[str, Any], 
                                  resume_created: bool = True, resume_pdf_path: str = None):
        """Update the CSV file to mark a job as having a resume created and add PDF path."""
        try:
            # Read all rows from the CSV
            rows = []
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames
                
                # Add is_resume_created column if it doesn't exist
                if 'is_resume_created' not in fieldnames:
                    fieldnames = list(fieldnames) + ['is_resume_created']
                
                # Add resume_pdf_path column if it doesn't exist
                if 'resume_pdf_path' not in fieldnames:
                    fieldnames = list(fieldnames) + ['resume_pdf_path']
                
                # Add is_applied column if it doesn't exist
                if 'is_applied' not in fieldnames:
                    fieldnames = list(fieldnames) + ['is_applied']
                
                for row in reader:
                    # Add is_resume_created field if it doesn't exist
                    if 'is_resume_created' not in row:
                        row['is_resume_created'] = 'false'
                    
                    # Add resume_pdf_path field if it doesn't exist
                    if 'resume_pdf_path' not in row:
                        row['resume_pdf_path'] = ''
                    
                    # Add is_applied field if it doesn't exist
                    if 'is_applied' not in row:
                        row['is_applied'] = 'false'
                    
                    # Update the matching job - use more robust matching
                    job_title_match = str(row.get('job_title', '')).strip() == str(job_data.get('job_title', '')).strip()
                    company_match = str(row.get('company', '')).strip() == str(job_data.get('company', '')).strip()
                    
                    # Also check external_url as a secondary match criterion
                    external_url_match = False
                    if 'external_url' in row and 'external_url' in job_data:
                        external_url_match = str(row.get('external_url', '')).strip() == str(job_data.get('external_url', '')).strip()
                    
                    if (job_title_match and company_match) or (external_url_match and external_url_match != ''):
                        row['is_resume_created'] = 'true' if resume_created else 'false'
                        if resume_pdf_path:
                            row['resume_pdf_path'] = resume_pdf_path
                            print(f"  → Updated resume_pdf_path for {job_data.get('job_title')} at {job_data.get('company')}")
                    
                    rows.append(row)
            
            # Write back to CSV
            with open(csv_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
        except Exception as e:
            print(f"Error updating CSV file: {e}")
    
    def update_csv_application_status(self, csv_path: str, job_data: Dict[str, Any], 
                                       is_applied: bool = True):
        """Update the CSV file to mark a job as applied."""
        try:
            # Read all rows from the CSV
            rows = []
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames
                
                # Add is_applied column if it doesn't exist
                if 'is_applied' not in fieldnames:
                    fieldnames = list(fieldnames) + ['is_applied']
                
                for row in reader:
                    # Add is_applied field if it doesn't exist
                    if 'is_applied' not in row:
                        row['is_applied'] = 'false'
                    
                    # Update the matching job - use more robust matching
                    job_title_match = str(row.get('job_title', '')).strip() == str(job_data.get('job_title', '')).strip()
                    company_match = str(row.get('company', '')).strip() == str(job_data.get('company', '')).strip()
                    
                    # Also check external_url as a secondary match criterion
                    external_url_match = False
                    if 'external_url' in row and 'external_url' in job_data:
                        external_url_match = str(row.get('external_url', '')).strip() == str(job_data.get('external_url', '')).strip()
                    
                    if (job_title_match and company_match) or (external_url_match and external_url_match != ''):
                        row['is_applied'] = 'true' if is_applied else 'false'
                        print(f"  → Marked job as applied: {job_data.get('job_title')} at {job_data.get('company')}")
                    
                    rows.append(row)
            
            # Write back to CSV
            with open(csv_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
        except Exception as e:
            print(f"Error updating CSV file with application status: {e}")
    
    def should_skip_job(self, job_data: Dict[str, Any]) -> bool:
        """Check if we should skip this job because a resume was already created."""
        is_resume_created = job_data.get('is_resume_created', '')
        # Handle None values and convert to string before calling lower()
        if is_resume_created is None:
            return False
        return str(is_resume_created).lower() == 'true'
    
    def has_applied_for_job(self, job_data: Dict[str, Any]) -> bool:
        """Check if we have already applied for this job."""
        is_applied = job_data.get('is_applied', '')
        # Handle None values and convert to string before calling lower()
        if is_applied is None:
            return False
        return str(is_applied).lower() == 'true'
    
    def read_resumes(self) -> List[Dict[str, str]]:
        """Read all resume files from the resumes directory."""
        resumes = []
        supported_extensions = ['.txt', '.md', '.docx', '.pdf', '.tex']
        
        if not self.resumes_dir.exists():
            print(f"Resume directory {self.resumes_dir} does not exist")
            return []
        
        for file_path in self.resumes_dir.iterdir():
            if (file_path.is_file() and 
                file_path.suffix.lower() in supported_extensions):
                try:
                    if file_path.suffix.lower() in ['.txt', '.md', '.tex']:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    elif file_path.suffix.lower() == '.docx':
                        # For docx files, you might need python-docx
                        try:
                            from docx import Document
                            doc = Document(file_path)
                            content = '\n'.join([para.text 
                                                 for para in doc.paragraphs])
                        except ImportError:
                            print(f"python-docx not installed, skipping {file_path}")
                            continue
                    else:
                        # Skip PDF files for now (would need PyPDF2 or similar)
                        print(f"PDF files not supported yet, skipping {file_path}")
                        continue
                    
                    resumes.append({
                        'filename': file_path.name,
                        'content': content
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
        
        print(f"Successfully read {len(resumes)} resumes")
        return resumes
    
    def create_tailored_resume(self, job_data: Dict[str, Any], 
                                resumes: List[Dict[str, str]]) -> str:
        """Use Gemini AI to create a tailored resume based on job description and 
        existing resumes."""
        
        # Prepare the prompt
        job_title = job_data.get('job_title', 'Unknown Position')
        company = job_data.get('company', 'Unknown Company')
        job_description = job_data.get('job_description', '')
        # Note: Currently reading from fixed files instead of using the resumes parameter
        # This allows for a consistent resume format from resume.md
        resumes_text = Path('resume.md').read_text()
        
        prompt = f"""
You are an expert resume writer specializing in creating highly targeted, ATS-optimized resumes 
in Markdown format. I need you to create a tailored resume for the following job application:

JOB TITLE: {job_title}
COMPANY: {company}

JOB DESCRIPTION:
{job_description}

EXISTING experiences:
{resumes_text}

PERSONAL INFO:
Name: {self.config.get('name', 'John Doe')}
Email: {self.config.get('email', 'john@doe.dev')}
Website: {self.config.get('website', 'doe.dev')}
GitHub: {self.config.get('github', 'github.com/johndoe')}

EXPANSION TECHNIQUES:
- Add specific numbers/metrics (%, time saved, user count, data volume)
- Include tools/frameworks used
- Mention business impact or results
- Add team size or scope
- Include additional technical details

BEFORE YOU START WRITING:
1. Remember: Every bullet must be 90-100 OR 180-190 characters for optimal PDF rendering
2. The ideal bullet length is 90-100 characters
3. Try not to make bullet length less than 90 characters
4. Plan to write a mix of short and long bullets for variety
5. For complex achievements, plan to write 180-190 char bullets
6. For simple achievements, keep them at 90-100 chars
7. NEVER write bullets between 101-179 characters

INSTRUCTIONS:

1. ANALYZE THE JOB REQUIREMENTS:
   - Extract specific technologies, frameworks, languages, and tools mentioned
   - Identify key responsibilities, seniority level, and required experience
   - Note any specific methodologies (Agile, TDD, CI/CD, etc.)
   - Look for keywords that appear multiple times - these are high priority
   - Identify the core problem they're trying to solve (performance, scale, user experience, etc.)
   
   JOB MATCHING APPROACH:
   - Find the 3-5 most important requirements from the job description
   - Map these to similar work you've done in your experience
   - Subtly emphasize these connections without being obvious
   - Example: If they mention "iOS graphics" and "performance", highlight any graphics work
     and performance optimizations you've done, even if they were minor parts of larger projects

2. CHRONOLOGICAL ACCURACY:
   - NEVER claim experience with technologies that didn't exist during that employment period
   - Match technology adoption timelines (e.g., SwiftUI only from 2019+)
   - Keep the EXACT same employers and date ranges from existing resumes

3. EXPERIENCE SECTION TAILORING:
   - 3-4 bullet points per job maximum
   - STRONGLY PREFER 90-100 character bullets (aim for at least 3 out of 4 bullets to be 90-100)
   - Only use 180-190 character bullets for truly complex achievements that cannot be simplified
   - Each bullet MUST be counted for character length
   - Lead with strong action verbs and quantifiable achievements
   - Be concise and impactful - say more with less
   - Feel free to write it however you think to achieve a match with the job description,
     just make sure it would match the experience job title
   - Make sure to reference only 1 job title per job company
   - DO NOT include location information for any jobs
   - DO NOT indent bullet points - they should start at the beginning of the line
   - Put dates on the same line as job title/company using pipe separator (|)
   
   SUBTLE CUSTOMIZATION STRATEGY:
   - For your MOST RECENT position: Emphasize technologies and skills from the job description
   - For ONE other relevant position: Subtly reframe accomplishments to highlight job-relevant
     skills
   - Examples of subtle edits:
     • If job asks for "performance optimization" → mention specific optimizations you did
     • If job asks for "team leadership" → emphasize any mentoring or leading you did
     • If job asks for specific frameworks → naturally incorporate them where you used them
   - Keep edits truthful - only highlight what you actually did, just frame it relevantly
   - Maintain the core responsibilities but adjust emphasis and technical details

4. SKILLS SECTION:
   - Prioritize technologies mentioned in the job description
   - Keep skill lists SHORT to prevent overflow - max 8-10 items per category
   - Each skill line must be under 100 characters

5. PROJECTS SECTION:
   - Include ONLY 1 PROJECT - no more, no less
   - Choose the most relevant project that aligns with the job description
   - 2-3 bullet points for the project (following the same 90-100 or 180-190 character rules)
   - Focus on technologies and outcomes that match the job requirements
   - Include a brief project title and date

6. MARKDOWN OUTPUT FORMAT:
   
   # [Full Name]
   
   [Email] • [Website] • [GitHub]
   
   ## Experience
   
   ### [Job Title] - [Company] | [Start Date] - [End Date]
   
   - [Bullet point 1 - exactly 90-100 or 180-190 characters]
   - [Bullet point 2 - exactly 90-100 or 180-190 characters]
   - [Bullet point 3 - exactly 90-100 or 180-190 characters]
   
   ### [Previous Job Title] - [Company] | [Start Date] - [End Date]
   
   - [Bullet points following same rules]
   
   ## Education
   
   ### [Degree] - [University] | [Graduation Date]
   *GPA: [X.XX]*
   
   ## Projects
   
   ### [Project Name] | [Technologies Used]
   *[Link to GitHub/Demo]*
   
   - [Bullet point about the project - 90-100 or 180-190 chars]
   - [Another bullet point if needed - 90-100 or 180-190 chars]
   
   ## Skills
   
   **Languages:** [List relevant languages from job description]
   **Frameworks:** [List relevant frameworks]
   **Tools & Technologies:** [List other relevant tools]

7. OUTPUT REQUIREMENTS:
   - Return ONLY the complete Markdown resume
   - No explanations, comments, or metadata
   - Use clean, professional Markdown formatting
   - Ensure all links are properly formatted
   
8. CRITICAL FORMATTING REQUIREMENTS:
   - Use proper Markdown headers (# for h1, ## for h2, ### for h3)
   - Use **bold** for emphasis on important keywords
   - Use *italics* ONLY for GPA and project links
   - Ensure proper spacing between sections
   - Use bullet points (-) for all lists
   - DO NOT indent bullet points - start them at the beginning of the line
   - NO location information in experience section
   - Dates go on same line as titles using pipe separator (|)

FINAL VALIDATION CHECKLIST (MANDATORY):
Before submitting, you MUST validate EVERY single bullet point:

CHARACTER COUNTING PROCESS:
1. For EACH bullet point in your resume:
   - Count EVERY character including spaces, punctuation, numbers
   - If count is 90-100: ✅ VALID
   - If count is 180-190: ✅ VALID
   - If count is 101-179: ❌ STOP! GO BACK AND EXPAND TO 180-190
   - If count is under 90: ❌ STOP! ADD MORE DETAIL TO REACH 90-100
   - If count is over 190: ❌ STOP! TRIM DOWN TO 180-190

2. DO NOT SUBMIT until ALL bullets are either 90-100 or 180-190 characters.

"""
        max_retries = 3
        retry_count = 0
        base_wait_time = 60  # Start with 60 seconds
        
        while retry_count < max_retries:
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    retry_count += 1
                    if retry_count < max_retries:
                        # Extract retry delay from error if available
                        retry_delay = base_wait_time
                        if "retryDelay" in error_str:
                            # Try to extract the delay value
                            import re
                            delay_match = re.search(r"retryDelay.*?(\d+)s", error_str)
                            if delay_match:
                                retry_delay = int(delay_match.group(1))
                        
                        wait_time = retry_delay * retry_count  # Exponential backoff
                        print(f"\n⏳ Rate limit hit. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                        print(f"   (Error: API quota exceeded)")
                        
                        # Show countdown
                        for i in range(wait_time, 0, -10):
                            print(f"   Resuming in {i} seconds...", end='\r')
                            time.sleep(min(10, i))
                        print()  # Clear the line
                        
                        continue
                    else:
                        print(f"\n❌ Rate limit error persists after {max_retries} retries")
                        print("   Consider waiting longer or checking your API quota")
                        return ""
                else:
                    print(f"Error generating tailored resume: {e}")
                    self.last_error = str(e)
                    return ""
        
        return ""
    
    def clean_markdown_output(self, markdown_content: str) -> str:
        """Remove markdown code fences from AI output."""
        import re
        
        # Remove ```markdown at the beginning
        markdown_content = re.sub(r'^```markdown\s*\n?', '', markdown_content, flags=re.MULTILINE)
        
        # Remove trailing ```
        markdown_content = re.sub(r'\n?```\s*$', '', markdown_content, flags=re.MULTILINE)
        
        # Remove any remaining ``` that might be in the middle
        markdown_content = re.sub(r'```', '', markdown_content)
        
        return markdown_content.strip()
    
    def save_markdown_resume(self, markdown_content: str, job_data: Dict[str, Any]) -> str:
        """Save the tailored markdown resume to a file and convert to PDF."""
        job_title = (job_data.get('job_title', 'Unknown_Position')
                     .replace('/', '_').replace(' ', '_'))
        company = (job_data.get('company', 'Unknown_Company')
                   .replace('/', '_').replace(' ', '_'))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{job_title}_{company}_{timestamp}"
        markdown_file = self.markdown_output_dir / f"{filename}.md"
        pdf_file = self.pdf_output_dir / f"{filename}.pdf"
        
        try:
            # Clean up markdown formatting from AI output
            cleaned_content = self.clean_markdown_output(markdown_content)
            
            # Save Markdown file
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"Markdown file saved: {markdown_file.name}")
            
            # Convert Markdown to PDF using the converter
            pdf_path = self.pdf_converter.convert(markdown_file, pdf_file)
            
            if pdf_path:
                print(f"✓ PDF generated: {Path(pdf_path).name}")
                return str(pdf_path)
            else:
                print(f"⚠ PDF conversion failed.")
                print(f"Markdown file available: {markdown_file.name}")
                # Return the Markdown file path to indicate partial success
                return str(markdown_file)
                
        except Exception as e:
            print(f"Error saving resume: {e}")
            # If we at least saved the markdown file, return its path
            if markdown_file.exists():
                return str(markdown_file)
            else:
                return ""  # Complete failure - no file created
    
    
    def process_jobs(self, csv_path: str, limit: int = None):
        """Process jobs from CSV and create tailored resumes."""
        # Read jobs from CSV
        jobs = self.read_csv(csv_path)
        if not jobs:
            print("No jobs to process")
            return
        
        # Read existing resumes
        resumes = self.read_resumes()
        if not resumes:
            print("No resumes found in the specified directory")
            return
        
        # Filter out jobs that already have resumes created
        jobs_to_process = []
        skipped_count = 0
        for job in jobs:
            if self.should_skip_job(job):
                skipped_count += 1
                continue
            jobs_to_process.append(job)
        
        if skipped_count > 0:
            print(f"Skipped {skipped_count} jobs that already have resumes created")
        
        if not jobs_to_process:
            print("No new jobs to process (all jobs already have resumes created)")
            return
        
        # Limit the number of jobs to process if specified
        if limit:
            jobs_to_process = jobs_to_process[:limit]
            print(f"Processing first {limit} jobs from {len(jobs_to_process)} remaining jobs")
        
        # Track progress
        successful_resumes = 0
        failed_resumes = 0
        rate_limit_delays = 0
        
        # Process each job
        for i, job in enumerate(jobs_to_process, 1):
            print(f"\nProcessing job {i}/{len(jobs_to_process)}: "
                  f"{job.get('job_title', 'Unknown')} at {job.get('company', 'Unknown')}")
            
            # Skip if no job description
            if not job.get('job_description'):
                print("Skipping job with no description")
                failed_resumes += 1
                continue
            
            # Create tailored markdown resume
            tailored_resume = self.create_tailored_resume(job, resumes)
            if tailored_resume:
                saved_path = self.save_markdown_resume(tailored_resume, job)
                if saved_path:
                    # Only mark as successful if PDF was generated
                    if saved_path.endswith('.pdf'):
                        print(f"✓ Created tailored resume: {saved_path}")
                        self.update_csv_resume_status(csv_path, job, True, saved_path)
                        print("✓ Updated CSV with resume status and PDF path")
                        successful_resumes += 1
                    else:
                        # Markdown file was created but PDF conversion failed
                        print(f"⚠️  Markdown created but PDF conversion failed: {saved_path}")
                        # Still mark as resume_created=true since we have the markdown
                        self.update_csv_resume_status(csv_path, job, True, saved_path)
                        successful_resumes += 1
                else:
                    print("✗ Failed to save resume")
                    failed_resumes += 1
            else:
                print("✗ Failed to generate tailored resume")
                failed_resumes += 1
                # Check if it was a rate limit issue
                if "exceeded your current quota" in str(self.last_error):
                    rate_limit_delays += 1
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 Resume Tailoring Summary:")
        print(f"   ✅ Successful: {successful_resumes}")
        print(f"   ❌ Failed: {failed_resumes}")
        if rate_limit_delays > 0:
            print(f"   ⏳ Rate limit delays: {rate_limit_delays}")
            print(f"\n💡 Tip: If you hit rate limits, wait a few minutes and run again.")
            print(f"   The script will skip jobs that already have resumes.")
        print(f"{'='*60}")

def find_latest_csv_file(directory: str = ".") -> str:
    """Find the most recently modified CSV file in the specified directory."""
    import glob
    
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    if not csv_files:
        return None
    
    # Sort by modification time, most recent first
    latest_csv = max(csv_files, key=os.path.getmtime)
    return latest_csv

def main():
    parser = argparse.ArgumentParser(
        description='Create tailored resumes based on job descriptions')
    parser.add_argument('--csv-path', 
                        help='Path to the CSV file containing job data. If not provided, uses the latest CSV file in current directory')
    parser.add_argument('--resumes-dir', 
                        default='/Users/ismatullamansurov/Documents/Latex Resumes', 
                        help='Path to directory containing existing resumes')
    parser.add_argument('--limit', type=int, help='Limit the number of jobs to process')
    
    args = parser.parse_args()
    
    # Determine which CSV file to use
    csv_path = args.csv_path
    if not csv_path:
        # Find the latest CSV file in the current directory
        csv_path = find_latest_csv_file()
        if not csv_path:
            print("Error: No CSV files found in the current directory")
            print("Please specify a CSV file with --csv-path or ensure there's at least one CSV file in the current directory")
            sys.exit(1)
        print(f"No CSV file specified. Using the latest CSV file: {os.path.basename(csv_path)}")
    
    # Validate CSV file exists
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    try:
        tailor = ResumeTailor(args.resumes_dir)
        tailor.process_jobs(csv_path, args.limit)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()