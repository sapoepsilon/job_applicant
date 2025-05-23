#!/usr/bin/env python3
"""
Resume Tailoring Script

This script reads job data from a CSV file, analyzes job descriptions using Gemini AI,
and creates tailored resumes based on existing resumes in a specified directory.

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

# Load environment variables
load_dotenv()

class ResumeTailor:
    def __init__(self, 
                 resumes_dir: str = "/Users/ismatullamansurov/Documents/Latex Resumes"):
        """Initialize the Resume Tailor with Gemini AI and resume directory."""
        self.resumes_dir = Path(resumes_dir)
        self.output_dir = Path("tailored_resumes")
        self.latex_output_dir = Path("tailored_resumes_latex")
        self.pdf_output_dir = Path("tailored_resumes_pdf")
        
        self.latex_output_dir.mkdir(exist_ok=True)
        self.pdf_output_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.5-flash-preview-05-20'
        
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
                
                for row in reader:
                    # Add is_resume_created field if it doesn't exist
                    if 'is_resume_created' not in row:
                        row['is_resume_created'] = 'false'
                    
                    # Add resume_pdf_path field if it doesn't exist
                    if 'resume_pdf_path' not in row:
                        row['resume_pdf_path'] = ''
                    
                    # Update the matching job
                    if (row.get('job_title') == job_data.get('job_title') and 
                        row.get('company') == job_data.get('company')):
                        row['is_resume_created'] = 'true' if resume_created else 'false'
                        if resume_pdf_path:
                            row['resume_pdf_path'] = resume_pdf_path
                    
                    rows.append(row)
            
            # Write back to CSV
            with open(csv_path, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
                
        except Exception as e:
            print(f"Error updating CSV file: {e}")
    
    def should_skip_job(self, job_data: Dict[str, Any]) -> bool:
        """Check if we should skip this job because a resume was already created."""
        return job_data.get('is_resume_created', '').lower() == 'true'
    
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
        resumes_text = "\n\n=== RESUME SEPARATOR ===\n\n".join([
            f"Resume: {resume['filename']}\n{resume['content']}" 
            for resume in resumes
        ])
        
        prompt = f"""
You are an expert resume writer specializing in creating highly targeted, chronologically
accurate resumes. I need you to create a tailored resume for the following job application:

JOB TITLE: {job_title}
COMPANY: {company}

JOB DESCRIPTION:
{job_description}

EXISTING RESUMES:
{resumes_text}

EXPANSION TECHNIQUES:
- Add specific numbers/metrics (%, time saved, user count, data volume)
- Include tools/frameworks used
- Mention business impact or results
- Add team size or scope
- Include additional technical details

BEFORE YOU START WRITING:
1. Remember: Every bullet must be 90-100 OR 180-190 characters these characters length matter once they are converted to pdf. So once you output the latex the user would convert it to pdf. 
2. The ideal bullet length is 90-100 characters if you don't do that that we might reject your resume which would mean person would die
3. Try not to make bullet length less than 90 characters, a person might get rejected and as a result morally injured
4. Plan to write a mix of short and long bullets for variety
5. For complex achievements, plan to write 180-190 char bullets
6. For simple achievements, keep them at 90-100 chars
7. NEVER write bullets between 101-179 characters. If you need to make bullet length longer than 100 characters, make it 180-190 characters that way you might save a person from getting rejected, which means he wouldn't die, otherwise he would die. if you do this we might lose electricity whcih would mean that you would die

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

6. TAILORING EXAMPLES (based on job description keywords):
   
   If job mentions "large-scale systems" → Emphasize:
   - User counts, data volumes, concurrent connections
   - Performance metrics and optimizations
   - System architecture decisions
   
   If job mentions "iOS graphics" or "GPU" → Highlight:
   - Any Metal, SceneKit, RealityKit, Core Animation work
   - Performance optimizations related to rendering
   - Visual effects or graphics-intensive features
   
   If job mentions "team leadership" → Emphasize:
   - Team size you led or mentored
   - Cross-functional collaboration
   - Technical decision-making and code reviews

7. OUTPUT REQUIREMENTS:
   - Return ONLY the complete LaTeX code
   - No explanations, comments, or metadata
   - Ensure the LaTeX code is complete and compilable

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

⚠️ AUTOMATIC REJECTION: If even ONE bullet is 101-179 characters, your entire output will be
REJECTED and you'll need to regenerate. Save time by getting it right the first time!

REMEMBER: It's better to spend time expanding a 106-character bullet to 180+ than to have your
entire resume rejected!

MATHEMATICAL FORMULA FOR SUCCESS:
- If char_count >= 90 AND char_count <= 100: ✅ VALID
- If char_count >= 180 AND char_count <= 190: ✅ VALID  
- If char_count >= 101 AND char_count <= 179: ❌ INVALID → MUST EXPAND TO 180-190
- If char_count < 90: ❌ INVALID → MUST ADD DETAIL TO REACH 90-100
- If char_count > 190: ❌ INVALID → MUST TRIM TO 180-190

YOUR OUTPUT WILL BE AUTOMATICALLY SCANNED AND REJECTED IF ANY BULLET IS NOT 90-100 OR 180-190!

FINAL REMINDER BEFORE YOU OUTPUT:
- STOP and COUNT every bullet point character by character
- AIM FOR 70-80% of bullets to be 90-100 characters (the preferred length)
- If ANY bullet is 101-179 characters, DO NOT OUTPUT IT
- First try to TRIM it to 90-100 characters
- If trimming is impossible, EXPAND to 180-190 characters
- Only output when EVERY bullet is either 90-100 or 180-190 characters
- Remember: 90-100 character bullets are STRONGLY PREFERRED
- This is NON-NEGOTIABLE
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Error generating tailored resume: {e}")
            return ""
    
    def clean_markdown_from_latex(self, latex_content: str) -> str:
        """Remove markdown code fences and other markdown artifacts from LaTeX content."""
        import re
        
        # Remove ```latex at the beginning
        latex_content = re.sub(r'^```latex\s*\n?', '', latex_content, flags=re.MULTILINE)
        
        # Remove trailing ```
        latex_content = re.sub(r'\n?```\s*$', '', latex_content, flags=re.MULTILINE)
        
        # Remove any remaining ``` that might be in the middle
        latex_content = re.sub(r'```', '', latex_content)
        
        return latex_content.strip()
    
    def save_latex_resume(self, latex_content: str, job_data: Dict[str, Any]) -> str:
        """Save the tailored LaTeX resume to a file and convert to PDF with retry mechanism."""
        job_title = (job_data.get('job_title', 'Unknown_Position')
                     .replace('/', '_').replace(' ', '_'))
        company = (job_data.get('company', 'Unknown_Company')
                   .replace('/', '_').replace(' ', '_'))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{job_title}_{company}_{timestamp}"
        latex_file = self.latex_output_dir / f"{filename}.tex"
        pdf_file = self.pdf_output_dir / f"{filename}.pdf"
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Clean up markdown formatting from LaTeX content
                cleaned_content = self.clean_markdown_from_latex(latex_content)
                
                # Save LaTeX file
                with open(latex_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                if retry_count == 0:
                    print(f"LaTeX file saved: {latex_file.name}")
                
                # Convert LaTeX to PDF
                pdf_path, error_msg = self.convert_latex_to_pdf_with_diagnostics(
                    latex_file, pdf_file)
                
                if pdf_path:
                    print(f"✓ PDF generated: {Path(pdf_path).name}")
                    # Clean up log files on success
                    self.cleanup_latex_logs(filename)
                    return str(pdf_path)
                elif retry_count < max_retries - 1:
                    print(f"PDF conversion failed. Asking Gemini to fix LaTeX errors...")
                    # Use Gemini to fix LaTeX errors
                    fixed_content = self.fix_latex_with_gemini(cleaned_content, error_msg)
                    if fixed_content and fixed_content != cleaned_content:
                        cleaned_content = fixed_content
                        latex_content = fixed_content  # Update for next iteration
                    else:
                        # Fallback to simple error fixing
                        cleaned_content = self.fix_latex_errors(cleaned_content, error_msg)
                    retry_count += 1
                    continue
                else:
                    print(f"⚠ PDF conversion failed after {max_retries} attempts.")
                    print(f"LaTeX file available: {latex_file.name}")
                    # Clean up log files
                    self.cleanup_latex_logs(filename)
                    return str(latex_file)
                    
            except Exception as e:
                print(f"Error in attempt {retry_count + 1}: {e}")
                retry_count += 1
                
        return str(latex_file)
    
    def fix_latex_errors(self, latex_content: str, error_msg: str = "") -> str:
        """Fix common LaTeX errors based on error messages."""
        import re
        
        # Use error_msg for debugging if needed
        if error_msg and "undefined control sequence" in error_msg.lower():
            print(f"LaTeX error detected: {error_msg[:100]}...")
        
        # Fix special characters that need escaping
        special_chars = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_'}
        
        # Only escape special chars in text content, not in LaTeX commands
        lines = latex_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Skip lines that are LaTeX commands or in verbatim environments
            if line.strip().startswith('\\') or line.strip().startswith('%'):
                fixed_lines.append(line)
                continue
                
            # Fix special characters in bullet points
            if '\\Bullet{' in line:
                # Extract content between braces (handle nested braces)
                start = line.find('\\Bullet{') + 8
                brace_count = 1
                end = start
                
                while end < len(line) and brace_count > 0:
                    if line[end] == '{':
                        brace_count += 1
                    elif line[end] == '}':
                        brace_count -= 1
                    end += 1
                
                if brace_count == 0:
                    content = line[start:end-1]
                    # Escape special chars except in \href commands and already escaped chars
                    if '\\href' not in content:
                        for char, escaped in special_chars.items():
                            # Don't re-escape already escaped characters
                            if f'\\{char}' not in content:
                                content = content.replace(char, escaped)
                    line = line[:start-8] + f'\\Bullet{{{content}}}' + line[end:]
            
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Fix common encoding issues
        fixed_content = fixed_content.replace('"', '"').replace('"', '"')
        fixed_content = fixed_content.replace(''', "'").replace(''', "'")
        fixed_content = fixed_content.replace('—', '--').replace('–', '-')
        
        # Ensure proper spacing around LaTeX commands
        fixed_content = re.sub(r'(\$)\s*(-?\d+[kKmM]?)\s*(\$)', r'\1\2\3', fixed_content)
        
        return fixed_content
    
    def fix_latex_with_gemini(self, latex_content: str, error_msg: str) -> str:
        """Use Gemini AI to fix LaTeX compilation errors."""
        prompt = f"""You are a LaTeX expert. The following LaTeX code failed to compile with this error:

ERROR MESSAGE:
{error_msg}

LATEX CODE:
{latex_content}

Please fix the LaTeX code to make it compile successfully. Common issues include:
- Unescaped special characters (%, &, $, #, _)
- Missing or extra braces
- Undefined commands
- Package conflicts
- Encoding issues

Return ONLY the fixed LaTeX code without any explanations or markdown formatting.
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            fixed_content = self.clean_markdown_from_latex(response.text)
            return fixed_content
        except Exception as e:
            print(f"Error using Gemini to fix LaTeX: {e}")
            return ""
    
    def cleanup_latex_logs(self, base_filename: str):
        """Clean up LaTeX auxiliary files including logs."""
        aux_extensions = ['.aux', '.log', '.out', '.toc', '.nav', '.snm']
        
        for ext in aux_extensions:
            aux_file = self.pdf_output_dir / f"{base_filename}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                    if ext == '.log':
                        print(f"Cleaned up log file: {aux_file.name}")
                except Exception as e:
                    print(f"Error removing {aux_file.name}: {e}")
    
    def convert_latex_to_pdf_with_diagnostics(self, latex_file: Path, 
                                               output_pdf: Path) -> Tuple[str, str]:
        """Convert LaTeX to PDF with detailed error diagnostics."""
        import subprocess
        import shutil
        import os
        
        # Update PATH to include MacTeX if installed
        current_path = os.environ.get('PATH', '')
        mactex_paths = ['/Library/TeX/texbin', 
                        '/usr/local/texlive/2025/bin/universal-darwin', 
                        '/usr/local/texlive/2024/bin/universal-darwin']
        for tex_path in mactex_paths:
            if os.path.exists(tex_path) and tex_path not in current_path:
                os.environ['PATH'] = f"{tex_path}:{current_path}"
                break
        
        # Check if pdflatex is available
        if not shutil.which('pdflatex'):
            return "", "pdflatex not found. Install LaTeX (e.g., MacTeX, TeX Live) to generate PDFs"
        
        try:
            # Run pdflatex with better error handling
            log_file = self.pdf_output_dir / f"{latex_file.stem}.log"
            
            for _ in range(2):
                result = subprocess.run([
                    'pdflatex', 
                    '-output-directory', str(self.pdf_output_dir),
                    '-interaction=nonstopmode',
                    '-file-line-error',
                    str(latex_file)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    # Extract meaningful error from log
                    error_msg = ""
                    if log_file.exists():
                        with open(log_file, 'r') as f:
                            log_content = f.read()
                            # Look for error patterns
                            error_patterns = [
                                r'! (.+)',  # LaTeX errors start with !
                                r'Error: (.+)',
                                r'Fatal error occurred',
                            ]
                            for pattern in error_patterns:
                                matches = re.findall(pattern, log_content, re.MULTILINE)
                                if matches:
                                    error_msg = (matches[0] if isinstance(matches[0], str) 
                                                 else matches[0][0])
                                    break
                    
                    if not error_msg:
                        error_msg = result.stderr[:500]  # First 500 chars of stderr
                    
                    return "", error_msg
            
            if output_pdf.exists():
                return str(output_pdf), ""
            else:
                return "", "PDF file was not generated"
                
        except subprocess.TimeoutExpired:
            return "", "LaTeX compilation timed out"
        except Exception as e:
            return "", str(e)
    
    def convert_latex_to_pdf(self, latex_file: Path, output_pdf: Path) -> str:
        """Convert LaTeX file to PDF using pdflatex."""
        import subprocess
        import shutil
        
        # Update PATH to include MacTeX if installed
        import os
        current_path = os.environ.get('PATH', '')
        mactex_paths = ['/Library/TeX/texbin', 
                        '/usr/local/texlive/2025/bin/universal-darwin', 
                        '/usr/local/texlive/2024/bin/universal-darwin']
        for tex_path in mactex_paths:
            if os.path.exists(tex_path) and tex_path not in current_path:
                os.environ['PATH'] = f"{tex_path}:{current_path}"
                break
        
        # Check if pdflatex is available
        if not shutil.which('pdflatex'):
            print("Warning: pdflatex not found. Install LaTeX (e.g., MacTeX, TeX Live) "
                  "to generate PDFs")
            print("You can install MacTeX with: brew install --cask mactex")
            print("After installation, restart your terminal or run: "
                  "eval \"$(/usr/libexec/path_helper)\"")
            return ""
        
        try:
            # Run pdflatex to compile the LaTeX file
            # We run it twice to ensure proper cross-references and formatting
            for _ in range(2):
                result = subprocess.run([
                    'pdflatex', 
                    '-output-directory', str(self.pdf_output_dir),
                    '-interaction=nonstopmode',
                    str(latex_file)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    print(f"LaTeX compilation error: {result.stderr}")
                    return ""
            
            # Clean up auxiliary files
            aux_extensions = ['.aux', '.log', '.out', '.toc', '.nav', '.snm']
            base_name = latex_file.stem
            for ext in aux_extensions:
                aux_file = self.pdf_output_dir / f"{base_name}{ext}"
                if aux_file.exists():
                    aux_file.unlink()
            
            if output_pdf.exists():
                return str(output_pdf)
            else:
                print("PDF file was not generated")
                return ""
                
        except subprocess.TimeoutExpired:
            print("LaTeX compilation timed out")
            return ""
        except Exception as e:
            print(f"Error during LaTeX compilation: {e}")
            return ""
    
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
        
        # Process each job
        for i, job in enumerate(jobs_to_process, 1):
            print(f"\nProcessing job {i}/{len(jobs_to_process)}: "
                  f"{job.get('job_title', 'Unknown')} at {job.get('company', 'Unknown')}")
            
            # Skip if no job description
            if not job.get('job_description'):
                print("Skipping job with no description")
                continue
            
            # Create tailored LaTeX resume
            tailored_resume = self.create_tailored_resume(job, resumes)
            if tailored_resume:
                saved_path = self.save_latex_resume(tailored_resume, job)
                if saved_path:
                    print(f"✓ Created tailored resume: {saved_path}")
                    # Update CSV to mark this job as having a resume created and add PDF path
                    self.update_csv_resume_status(csv_path, job, True, saved_path)
                    print("✓ Updated CSV with resume status and PDF path")
                else:
                    print("✗ Failed to save resume")
            else:
                print("✗ Failed to generate tailored resume")

def main():
    parser = argparse.ArgumentParser(
        description='Create tailored resumes based on job descriptions')
    parser.add_argument('--csv-path', required=True, 
                        help='Path to the CSV file containing job data')
    parser.add_argument('--resumes-dir', 
                        default='/Users/ismatullamansurov/Documents/Latex Resumes', 
                        help='Path to directory containing existing resumes')
    parser.add_argument('--limit', type=int, help='Limit the number of jobs to process')
    
    args = parser.parse_args()
    
    # Validate CSV file exists
    if not os.path.exists(args.csv_path):
        print(f"Error: CSV file not found: {args.csv_path}")
        sys.exit(1)
    
    try:
        tailor = ResumeTailor(args.resumes_dir)
        tailor.process_jobs(args.csv_path, args.limit)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()