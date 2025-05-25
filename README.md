# Job Application Automation Tool

An intelligent browser automation tool that combines Playwright MCP (Model Context Protocol) with Google's Gemini API to automate job applications using natural language instructions.

## Features

- 🤖 **Natural Language Commands**: Tell the bot what to do in plain English
- 🌐 **Smart Browser Automation**: Powered by Playwright for reliable web interactions
- 📝 **Resume Tailoring**: Automatically customize resumes for specific job postings
- 🔍 **Job Scraping**: Extract job listings from various platforms
- 🚀 **Multiple Implementation Options**: Choose between direct MCP, LangChain, or browser-use approaches
- 🔑 **Credential Management**: Automatically saves and reuses login credentials for job sites

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

## Configuration

The application uses a `config.py` file for all configuration. To get started:

1. Copy the example configuration file:
   ```bash
   cp example.config.py config.py
   ```

2. Edit `config.py` with your personal information and preferences.

### Configuration Sections

1. **Personal Information**
   - Update your name, contact details, and professional profiles
   - Set your work authorization and visa status
   - Configure location and relocation preferences

2. **Playwright Settings**
   - Configure browser behavior (Chrome, Firefox, etc.)
   - Set up proxy and network settings if needed
   - Configure output directories for screenshots and traces

3. **Terminal Settings**
   - Configure terminal command execution if needed

### Security Note

The `config.py` file is included in `.gitignore` by default as it contains sensitive information. Never commit your actual `config.py` to version control.

For a complete reference of all available configuration options, see `example.config.py`.

## Usage

The application uses `config.py` for all configuration settings. Here are the main configuration options:

### Playwright MCP Configuration

All browser automation settings can be configured in `config.py` through the `PlaywrightConfig` class:

```python
class PlaywrightConfig:
    # Browser selection ("chromium", "firefox", "webkit", "msedge")
    BROWSER: str = "chromium"
    
    # Browser window settings
    HEADLESS: bool = False
    DEVICE: Optional[str] = None  # e.g., "iPhone 15"
    VIEWPORT_SIZE: Optional[str] = None  # e.g., "1280,720"
    USER_AGENT: Optional[str] = None
    
    # User data and profiles
    USER_DATA_DIR: Optional[str] = "~/Library/Caches/ms-playwright/chromium-1148"
    STORAGE_STATE: Optional[str] = None  # Path to storage state file
    
    # Network settings
    PROXY_SERVER: Optional[str] = None
    PROXY_BYPASS: Optional[str] = None
    IGNORE_HTTPS_ERRORS: bool = False
    
    # Security settings
    NO_SANDBOX: bool = True
    ALLOWED_ORIGINS: List[str] = []
    BLOCKED_ORIGINS: List[str] = []
    BLOCK_SERVICE_WORKERS: bool = False
    
    # Performance settings
    NO_IMAGE_RESPONSES: bool = False
    
    # Output settings
    OUTPUT_DIR: Optional[str] = None  # Directory for output files
    SAVE_TRACE: bool = False  # Whether to save Playwright Trace
```

### Terminal Configuration

The terminal controller can be configured through the `TerminalConfig` class:

```python
class TerminalConfig:
    COMMAND = "npx"
    ARGS = ["-y", "@wonderwhy-er/desktop-commander@latest"]
    ENV = None
```

### Credentials

Credentials are managed in `job_credentials.csv` by default. The path can be changed in `config.py`:

```python
# Project root directory
PROJECT_ROOT = Path(__file__).parent

# Credentials file path
CREDENTIALS_FILE = PROJECT_ROOT / "job_credentials.csv"
```

## Usage


   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Install LaTeX**
   ```bash
   brew install --cask mactex
   ```
   or run `./install_latex.sh`
6. **Install Playwright**

   ```bash
   npm install -g play
   ```

7. **Install Playwright dependencies**
   ```bash
   npm install
   ```
8. ** Create a resume.md file in the root directory**
   ```bash
   cp resume_example.md resume.md
   ```
   Fill your resume.md file with your information.w

## Usage

### Quick Start with Command Center (Recommended)

The easiest way to use this tool is through the command center:

```bash
python command_center.py
```

This gives you an interactive menu with options to:

1. **Complete Workflow**: Scrape jobs → Tailor resumes → Apply to jobs
2. **Individual Steps**: Run each component separately

### Complete Workflow Example

Here's a typical workflow for finding and applying to jobs:

1. **Find Jobs**: Scrape job listings from Hiring Cafe

   ```bash
   python hiring_cafe_scraper.py "iOS developer" 50
   ```

   This creates a CSV file (e.g., `ios_developer_jobs.csv`) with columns:

   - job_title, company, location, external_url, job_description, etc.

2. **Tailor Resumes**: Generate customized resumes for each job

   ```bash
   python resume_tailor.py --csv-path ios_developer_jobs.csv --limit 10
   ```

   This creates tailored PDFs in `tailored_resumes_pdf/` and updates the CSV with `resume_pdf_path`.

3. **Apply to Jobs**: Use the automation agent
   ```bash
   python job_applicant.py
   ```
   The agent will:
   - Show available CSV files and let you choose
   - Display job summary (total, already applied, ready to apply)
   - Apply to each job using the tailored resume
   - Update the CSV with application status

### Interacting with the Job Application Agent

When you run `job_applicant.py`, you'll get an interactive prompt where you can give natural language commands:

```
Job Application Automation Agent
================================
Type 'quit' to exit

What would you like me to do?
>
```

#### Example Commands

**Basic Navigation:**

```
> Go to linkedin.com
> Search for iOS developer jobs in San Francisco
> Click on the first job listing
```

**Job Application:**

```
> Fill out the application form with my information
> Upload my resume from tailored_resumes_pdf/company_name_resume.pdf
> Submit the application
```

**Complex Tasks:**

```
> Go to indeed.com and apply to the first 5 iOS developer jobs in New York
> Find remote React developer positions and save the URLs to a file
> Navigate to this job posting [URL] and check if I meet the requirements
```

**Data Extraction:**

```
> Extract the job requirements from this page
> Save the company names and job titles from the search results
> Take a screenshot of the application confirmation
```

#### Hiring Cafe Scraper

Scrape jobs from Hiring Cafe:

```bash
python hiring_cafe_scraper.py "job title" number_of_jobs

# Examples:
python hiring_cafe_scraper.py "software engineer" 100
python hiring_cafe_scraper.py "data scientist" 50
python hiring_cafe_scraper.py "product manager" 25
```

Output: Creates a CSV file named `job_title_jobs.csv` with columns:

- Company
- Job Title
- Location
- Job Link
- Posted Date

#### Resume Tailoring

Customize your resume for specific job postings:

```bash
python resume_tailor.py --csv-path jobs.csv --limit 10 --resumes-dir /path/to/resumes

# Example with all options:
python resume_tailor.py \
  --csv-path ios_developer_jobs.csv \
  --limit 20 \
  --resumes-dir ~/Documents/Resumes
```

Arguments:

- `--csv-path`: Path to the CSV file containing job listings
- `--limit`: Number of jobs to process (default: all)
- `--resumes-dir`: Path to directory containing LaTeX resume templates

Output:

- LaTeX files in `tailored_resumes_latex/`
- PDF files in `tailored_resumes_pdf/`
- Each resume is named: `CompanyName_JobTitle_Resume.pdf`

**Note**: Requires LaTeX (pdflatex) to be installed. Install with:

- macOS: `brew install --cask mactex` or run `./install_latex.sh`
- Linux: `sudo apt-get install texlive-full`

### Credential Management

The job application tool now includes automatic credential management to save time when applying to multiple jobs on the same platform:

**Features:**

- Automatically saves login credentials when you create an account
- Reuses existing credentials when applying to jobs on the same domain
- Stores credentials in `job_credentials.csv` with basic encoding
- Tracks when credentials were created and last used

**How it works:**

1. When applying to a job, the system checks if credentials exist for that domain
2. If credentials exist, they are used to log in automatically
3. If no credentials exist, a new account is created and the credentials are saved
4. The system extracts passwords from the Gemini response and saves them automatically

**Security Note:**
⚠️ The credentials are stored with basic base64 encoding, which is NOT secure encryption. This is for demonstration purposes only. In production:

- Use a proper password manager or encryption service
- Never commit `job_credentials.csv` to version control
- Consider using environment variables or secure vaults for credentials

**Credential File Structure:**
The `job_credentials.csv` file contains:

- `domain`: The main domain (e.g., "example.com")
- `username`: The email used for the account
- `password`: Base64-encoded password
- `created_date`: When the credentials were first saved
- `last_used`: When the credentials were last used
