# Job Application Automation Tool

An intelligent browser automation tool that combines Playwright MCP (Model Context Protocol) with Google's Gemini API to automate job applications using natural language instructions.

## Features

- 🤖 **Natural Language Commands**: Tell the bot what to do in plain English
- 🌐 **Smart Browser Automation**: Powered by Playwright for reliable web interactions
- 📝 **Resume Tailoring**: Automatically customize resumes for specific job postings
- 🔍 **Job Scraping**: Extract job listings from various platforms
- 🚀 **Multiple Implementation Options**: Choose between direct MCP, LangChain, or browser-use approaches

## Prerequisites

- Python 3.8+
- Node.js and npm
- Google Gemini API key
- LaTeX distribution (e.g., MacTeX, TeX Live) - Required for PDF generation in resume_tailor.py

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sapoepsilon/job_applicant.git
   cd job_applicant
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

### Main Job Application Script

#### Hiring Cafe Scraper

Scrape jobs from Hiring Cafe:

```bash
python hiring_cafe_scraper.py "job name" 10
```

the first argument is the job name and the second argument is the number of jobs to scrape

#### Resume Tailoring

Customize your resume for specific job postings:

```bash
python resume_tailor.py --csv-path ios_developer_jobs.csv --limit 10 --resumes-dir /path/to/your/resumes
```

Arguments:
- `--csv-path`: Path to the CSV file containing job listings
- `--limit`: Number of jobs to process
- `--resumes-dir`: Path to directory containing existing resumes (default: `/Users/ismatullamansurov/Documents/Latex Resumes`)

**Note**: This script requires a LaTeX distribution (pdflatex) to be installed for PDF generation. If pdflatex is not found, you'll see an error message directing you to install LaTeX (e.g., MacTeX for macOS, TeX Live for Linux).

The primary script that uses Playwright MCP with Gemini for job automation:

```bash
python job_applicant.py
```

This will:

1. Open a browser window
2. Navigate to job sites based on your instructions
3. Fill out applications automatically
4. Save application progress
