# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a job application automation system that combines browser automation capabilities with AI to help automate the job search and application process. The system consists of several interconnected components:

1. **Job Scraping**: Extract job listings from platforms like Hiring Cafe
2. **Resume Tailoring**: Automatically customize resumes based on job descriptions using Gemini AI
3. **Browser Automation**: Three different implementations for automating web interactions:
   - Direct MCP client with Gemini API (`job_applicant.py`)
   - LangChain with multiple MCP servers (`langchain_mcp.py`)
   - Browser-use library with planning capabilities (`langchain_browser_use.py`)

The system uses Google's Gemini API for natural language processing and Playwright for browser automation through the Model Context Protocol (MCP).

## Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Add GEMINI_API_KEY to .env file

# Install LaTeX for resume PDF generation (macOS)
./install_latex.sh
# Or manually: brew install --cask mactex
```

### Running the Scripts

**Command Center (Recommended):**
```bash
# Interactive menu for complete workflow
python command_center.py
# Options:
# 1. Scrape jobs and automatically tailor resumes
# 2. Scrape jobs only
# 3. Tailor resumes from existing CSV
# 4. Launch job application agent
```

**Individual Scripts:**
```bash
# Job Scraping
python hiring_cafe_scraper.py "job title" number_of_jobs
# Example: python hiring_cafe_scraper.py "iOS developer" 50

# Resume Tailoring
python resume_tailor.py --csv-path jobs.csv --limit 10 --resumes-dir /path/to/resume/templates

# Browser Automation
python job_applicant.py  # Main interactive agent
python langchain_mcp.py  # LangChain with multiple MCP servers
python langchain_browser_use.py --url https://example.com --query "Your task"
```

### Docker Commands
```bash
# Basic Docker run
docker-compose up job-applicant

# Interactive Docker with options
./docker-run.sh

# Chrome passthrough mode (for debugging)
docker-compose up job-applicant-dev
```

## Architecture

### Core Components

1. **MCP Server Integration**:
   - Playwright MCP (`@playwright/mcp`): Browser automation
   - Desktop Commander (`@wonderwhy-er/desktop-commander`): Terminal operations
   - Additional servers in `langchain_mcp.py`: Context7, PostgreSQL, iTerm, Filesystem, Todoist, Playwright
   - Gmail automation in `job_applicant.py`: `@gongrzhe/server-gmail-autoauth-mcp`

2. **Multi-Step Processing (`job_applicant.py`)**:
   - User prompt → Instruction generation (Gemini) → Execution (Gemini + tools) → Result
   - Maintains conversation context with function calls and results
   - Aggregates tools from multiple MCP sessions

3. **Resume Processing Pipeline**:
   - Reads job CSV → Extracts job details → Generates tailored LaTeX → Compiles to PDF
   - Supports .docx resume templates
   - Output: `tailored_resumes_latex/` and `tailored_resumes_pdf/`

### Key Dependencies

- **AI/LLM**: `google-genai>=1.15.0`, `langchain-google-genai==2.1.2`
- **Browser Automation**: `playwright>=1.40.0`, `browser-use==0.1.48`
- **MCP**: `mcp>=1.9.0`, `langchain-mcp-adapters>=0.1.1`
- **LangChain**: `langchain-core==0.3.49`, `langgraph>=0.4.5`
- **Data Processing**: `pandas>=2.0.0`, `python-docx>=0.8.11`

### File Structure

- `command_center.py`: Interactive menu system for complete workflow automation
- `job_applicant.py`: Main interactive agent with Gemini + MCP
- `langchain_mcp.py`: LangChain ReAct agent with 6 MCP servers
- `langchain_browser_use.py`: Browser-use agent with planning
- `hiring_cafe_scraper.py`: Job scraping from Hiring Cafe
- `resume_tailor.py`: AI-powered resume customization
- `job_extractor.py`: Helper for job data extraction
- `tailored_resumes_*/`: Output directories for resumes

## Development Guidelines

### Adding New MCP Servers

In `job_applicant.py`:
```python
new_server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@package/name@latest"],
    env=None,
)
# Add to sessions list in main()
```

### Debugging Browser Automation

1. Run with visible browser: `--headless=false` (langchain_browser_use.py)
2. Check browser console logs via MCP tools
3. Browser-use creates session GIFs in the working directory
4. For Chrome passthrough: Start Chrome with `--remote-debugging-port=9222`

### Context Management

The main agent (`job_applicant.py`) maintains:
- `function_calls`: List of all function call history
- `function_args`: Arguments for each function call
- `historic_text`: Accumulated text responses
- Current step tracking for complex multi-step tasks

### Error Handling

- LaTeX compilation errors: Ensure pdflatex is installed
- MCP connection issues: Verify npm packages are installed globally
- Gemini API errors: Check API key in .env file
- Browser timeouts: Add explicit waits in prompts