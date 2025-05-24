#!/usr/bin/env python3
"""
Job Application Command Center

A simple command-line interface to streamline the job application workflow:
1. Scrape jobs from Hiring Cafe
2. Automatically tailor resumes for scraped jobs
3. Apply to jobs using the automation agent

Usage:
    python command_center.py
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

class CommandCenter:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.resumes_dir = "/Users/ismatullamansurov/Documents/Latex Resumes"
        self.venv_path = self.project_root / "venv"
        self.python_executable = self.get_python_executable()
    
    def get_python_executable(self):
        """Get the appropriate Python executable, preferring venv if available."""
        venv_python = self.venv_path / "bin" / "python"
        if venv_python.exists():
            return str(venv_python)
        return sys.executable
        
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "="*60)
        print("🚀 Job Application Command Center")
        print("="*60)
        print("\n1. Scrape jobs and tailor resumes (complete workflow)")
        print("2. Scrape jobs only")
        print("3. Tailor resumes from existing CSV")
        print("4. Launch job application agent")
        print("5. Exit")
        print()
        
    def get_job_search_params(self):
        """Get job search parameters from user."""
        job_title = input("Enter job title to search for: ").strip()
        if not job_title:
            print("❌ Job title cannot be empty")
            return None, None
            
        while True:
            try:
                num_jobs = int(input("Number of jobs to scrape (default: 50): ").strip() or "50")
                if num_jobs <= 0:
                    print("❌ Number must be positive")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number")
                
        return job_title, num_jobs
    
    def scrape_jobs(self, job_title, num_jobs):
        """Run the hiring cafe scraper."""
        print(f"\n🔍 Scraping {num_jobs} '{job_title}' jobs from Hiring Cafe...")
        print("⏳ This may take a few minutes depending on the number of jobs...")
        print(f"Once we scrape a job, you will see {job_title}_jobs.csv file in the project directory")
        
        cmd = [
            self.python_executable,
            str(self.project_root / "hiring_cafe_scraper.py"),
            job_title,
            str(num_jobs)
        ]
        
        try:
            # Run with real-time output and longer timeout
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}  # Force unbuffered output
            )
            
            jobs_saved = 0
            # Stream output in real-time
            for line in process.stdout:
                # Add visual indicator for job saves
                if "data saved to CSV!" in line:
                    jobs_saved += 1
                    print(f"✨ [{jobs_saved}/{num_jobs}] {line}", end='', flush=True)
                elif "Extracted job data:" in line:
                    print(f"📊 {line}", end='', flush=True)
                elif "already scraped" in line:
                    print(f"⏭️  {line}", end='', flush=True)
                else:
                    print(line, end='', flush=True)
                
            process.wait()
            
            if process.returncode != 0:
                print(f"\n❌ Scraper exited with error code: {process.returncode}")
                return None
            
            # Extract the CSV filename from the scraper output
            csv_filename = f"{job_title.replace(' ', '_').lower()}_jobs.csv"
            csv_path = self.project_root / csv_filename
            
            if csv_path.exists():
                print(f"\n✅ Successfully scraped jobs to: {csv_filename}")
                return str(csv_path)
            else:
                print("\n❌ CSV file was not created")
                return None
                
        except Exception as e:
            print(f"\n❌ Error scraping jobs: {e}")
            return None
    
    def tailor_resumes(self, csv_path, limit=None):
        """Run the resume tailor on a CSV file."""
        print(f"\n📝 Tailoring resumes from: {Path(csv_path).name}")
        
        cmd = [
            self.python_executable,
            str(self.project_root / "resume_tailor.py"),
            "--csv-path", csv_path,
            "--resumes-dir", self.resumes_dir
        ]
        
        if limit:
            cmd.extend(["--limit", str(limit)])
            print(f"   Processing up to {limit} jobs")
        
        try:
            # Run with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env={**os.environ, 'PYTHONUNBUFFERED': '1'}  # Force unbuffered output
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(line, end='', flush=True)
                # Check for rate limit messages
                if "Rate limit hit" in line or "API quota exceeded" in line:
                    print("\n💡 Tip: The script will automatically retry after waiting.")
                
            process.wait()
            
            if process.returncode == 0:
                print("\n✅ Resume tailoring completed successfully!")
                return True
            else:
                print("\n❌ Resume tailoring failed")
                return False
                
        except Exception as e:
            print(f"❌ Error tailoring resumes: {e}")
            return False
    
    def scrape_and_tailor(self):
        """Scrape jobs and automatically tailor resumes."""
        job_title, num_jobs = self.get_job_search_params()
        if not job_title:
            return
            
        # Step 1: Scrape jobs
        csv_path = self.scrape_jobs(job_title, num_jobs)
        if not csv_path:
            print("❌ Job scraping failed. Cannot proceed with resume tailoring.")
            return
            
        # Step 2: Count jobs and start tailoring
        print(f"\n✅ Jobs scraped successfully!")
        
        # Count jobs in CSV to show user
        try:
            import csv
            with open(csv_path, 'r') as f:
                job_count = sum(1 for _ in csv.reader(f)) - 1  # Subtract header
            print(f"📊 Found {job_count} jobs in the CSV file")
        except:
            job_count = "all"
        
        # Step 3: Tailor resumes for all jobs
        print(f"\n🎯 Starting resume tailoring for {job_count} jobs...")
        self.tailor_resumes(csv_path, limit=None)
        
        # Step 4: Offer to launch job applicant
        response = input("\n🤖 Would you like to launch the job application agent? (y/n): ").strip().lower()
        if response == 'y':
            self.launch_job_applicant()
    
    def tailor_from_csv(self):
        """Tailor resumes from an existing CSV file."""
        # List available CSV files
        csv_files = list(self.project_root.glob("*_jobs.csv"))
        
        if not csv_files:
            print("❌ No job CSV files found in the project directory")
            return
            
        print("\n📁 Available CSV files:")
        for i, csv_file in enumerate(csv_files, 1):
            # Get file stats
            stat = csv_file.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            print(f"{i}. {csv_file.name} (Modified: {mod_time})")
            
        while True:
            try:
                choice = input("\nSelect CSV file number (or 0 to enter custom path): ").strip()
                if choice == "0":
                    csv_path = input("Enter full path to CSV file: ").strip()
                    if not Path(csv_path).exists():
                        print("❌ File not found")
                        continue
                    break
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(csv_files):
                        csv_path = str(csv_files[idx])
                        break
                    else:
                        print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a valid number")
                
        # Ask about limit
        while True:
            resume_limit = input("How many resumes to tailor? (Enter for all): ").strip()
            if not resume_limit:
                limit = None
                break
            try:
                limit = int(resume_limit)
                if limit <= 0:
                    print("❌ Number must be positive")
                    continue
                break
            except ValueError:
                print("❌ Please enter a valid number or press Enter for all")
                
        self.tailor_resumes(csv_path, limit)
    
    def launch_job_applicant(self):
        """Launch the job application agent."""
        # Check if any CSV files exist
        csv_files = list(self.project_root.glob("*_jobs.csv"))
        
        if not csv_files:
            print("\n⚠️  No job CSV files found!")
            print("💡 Tip: First scrape some jobs using option 1 or 2")
            return
        
        print("\n📁 Available job CSV files:")
        for i, csv_file in enumerate(csv_files, 1):
            # Get file stats
            stat = csv_file.stat()
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            
            # Count jobs in CSV
            try:
                import csv
                with open(csv_file, 'r') as f:
                    job_count = sum(1 for _ in csv.reader(f)) - 1  # Subtract header
                print(f"{i}. {csv_file.name} ({job_count} jobs, Modified: {mod_time})")
            except:
                print(f"{i}. {csv_file.name} (Modified: {mod_time})")
        
        print(f"\n💡 The job application agent will process jobs from these CSV files.")
        response = input("Continue? (Y/n): ").strip().lower()
        if response == 'n':
            return
            
        print("\n🤖 Launching job application agent...")
        print("="*60)
        
        cmd = [self.python_executable, str(self.project_root / "job_applicant.py")]
        
        try:
            # Run interactively
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\n\n👋 Job application agent closed")
        except Exception as e:
            print(f"❌ Error launching job applicant: {e}")
    
    def run(self):
        """Main command center loop."""
        print("\n🎯 Welcome to the Job Application Command Center!")
        print("This tool helps you automate your job search workflow.\n")
        
        while True:
            self.display_menu()
            choice = input("Select an option (1-5): ").strip()
            
            if choice == "1":
                self.scrape_and_tailor()
            elif choice == "2":
                job_title, num_jobs = self.get_job_search_params()
                if job_title:
                    csv_path = self.scrape_jobs(job_title, num_jobs)
                    if csv_path:
                        print(f"\n💡 Tip: You can tailor resumes later using option 3")
            elif choice == "3":
                self.tailor_from_csv()
            elif choice == "4":
                self.launch_job_applicant()
            elif choice == "5":
                print("\n👋 Goodbye! Good luck with your job search!")
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
            if choice in ["1", "2", "3"]:
                input("\nPress Enter to continue...")

def main():
    """Entry point for the command center."""
    try:
        center = CommandCenter()
        center.run()
    except KeyboardInterrupt:
        print("\n\n👋 Command Center closed. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()