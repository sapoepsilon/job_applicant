#!/usr/bin/env python3
"""
CSV Utility Functions for Job Application Tracking

This module provides utility functions for managing job application CSV files,
including updating application status and checking job statuses.
"""

import csv
from typing import Dict, Any, List, Optional
import os


def update_job_application_status(csv_path: str, job_data: Dict[str, Any], 
                                  is_applied: bool = True) -> bool:
    """
    Update the CSV file to mark a job as applied.
    
    Args:
        csv_path: Path to the CSV file
        job_data: Dictionary containing job information (must have 'job_title' and 'company')
        is_applied: Whether the job has been applied for (default: True)
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        # Read all rows from the CSV
        rows = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldnames = list(reader.fieldnames) if reader.fieldnames else []
            
            # Add is_applied column if it doesn't exist
            if 'is_applied' not in fieldnames:
                fieldnames = fieldnames + ['is_applied']
            
            for row in reader:
                # Add is_applied field if it doesn't exist
                if 'is_applied' not in row:
                    row['is_applied'] = 'false'
                
                # Update the matching job - use robust matching
                job_title_match = str(row.get('job_title', '')).strip() == str(job_data.get('job_title', '')).strip()
                company_match = str(row.get('company', '')).strip() == str(job_data.get('company', '')).strip()
                
                # Also check external_url as a secondary match criterion
                external_url_match = False
                if 'external_url' in row and 'external_url' in job_data:
                    external_url_match = str(row.get('external_url', '')).strip() == str(job_data.get('external_url', '')).strip()
                
                if (job_title_match and company_match) or (external_url_match and external_url_match != ''):
                    row['is_applied'] = 'true' if is_applied else 'false'
                    print(f"✓ Marked job as applied: {job_data.get('job_title')} at {job_data.get('company')}")
                
                rows.append(row)
        
        # Write back to CSV
        with open(csv_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        return True
        
    except Exception as e:
        print(f"Error updating CSV file with application status: {e}")
        return False


def check_if_applied(csv_path: str, job_data: Dict[str, Any]) -> bool:
    """
    Check if a job has already been applied for.
    
    Args:
        csv_path: Path to the CSV file
        job_data: Dictionary containing job information
    
    Returns:
        bool: True if already applied, False otherwise
    """
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Match the job
                job_title_match = str(row.get('job_title', '')).strip() == str(job_data.get('job_title', '')).strip()
                company_match = str(row.get('company', '')).strip() == str(job_data.get('company', '')).strip()
                
                if job_title_match and company_match:
                    is_applied = row.get('is_applied', '')
                    if is_applied is None:
                        return False
                    return str(is_applied).lower() == 'true'
                    
        return False
        
    except Exception as e:
        print(f"Error checking application status: {e}")
        return False


def get_unapplied_jobs(csv_path: str) -> List[Dict[str, Any]]:
    """
    Get list of jobs that haven't been applied for yet.
    
    Args:
        csv_path: Path to the CSV file
    
    Returns:
        List of job dictionaries that haven't been applied for
    """
    unapplied_jobs = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                is_applied = row.get('is_applied', '')
                if is_applied is None or str(is_applied).lower() != 'true':
                    unapplied_jobs.append(dict(row))
                    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    
    return unapplied_jobs


def get_jobs_with_resumes(csv_path: str) -> List[Dict[str, Any]]:
    """
    Get list of jobs that have resumes created but haven't been applied for.
    
    Args:
        csv_path: Path to the CSV file
    
    Returns:
        List of job dictionaries with resumes but not applied
    """
    jobs_with_resumes = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                is_resume_created = row.get('is_resume_created', '')
                is_applied = row.get('is_applied', '')
                
                # Check if resume is created but not applied
                has_resume = is_resume_created and str(is_resume_created).lower() == 'true'
                not_applied = not is_applied or str(is_applied).lower() != 'true'
                
                if has_resume and not_applied:
                    jobs_with_resumes.append(dict(row))
                    
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    
    return jobs_with_resumes


def find_latest_csv_file(directory: str = ".") -> Optional[str]:
    """
    Find the most recently modified CSV file in the specified directory.
    
    Args:
        directory: Directory to search in (default: current directory)
    
    Returns:
        Path to the latest CSV file, or None if no CSV files found
    """
    import glob
    
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    if not csv_files:
        return None
    
    # Sort by modification time, most recent first
    latest_csv = max(csv_files, key=os.path.getmtime)
    return latest_csv


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        
        # Show unapplied jobs
        unapplied = get_unapplied_jobs(csv_file)
        print(f"\nFound {len(unapplied)} unapplied jobs:")
        for job in unapplied[:5]:  # Show first 5
            print(f"  - {job.get('job_title')} at {job.get('company')}")
        
        # Show jobs with resumes ready to apply
        ready_to_apply = get_jobs_with_resumes(csv_file)
        print(f"\n{len(ready_to_apply)} jobs have resumes ready to apply")
    else:
        print("Usage: python csv_utils.py <csv_file>")