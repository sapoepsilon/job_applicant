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

4. **Install MCP packages**
   ```bash
   npm install -g @playwright/mcp
   npm install -g @wonderwhy-er/desktop-commander
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

### Main Job Application Script

The primary script that uses Playwright MCP with Gemini for job automation:

```bash
python job_applicant.py
```

This will:
1. Open a browser window
2. Navigate to job sites based on your instructions
3. Fill out applications automatically
4. Save application progress

### Alternative Implementations

#### LangChain with Multiple MCP Servers
```bash
python langchain_mcp.py
```

This version includes additional MCP servers for:
- File system operations
- PostgreSQL database access
- Terminal control
- Todo list management

#### Browser-Use with Planning
```bash
python langchain_browser_use.py
```

Command-line options:
```bash
# Start with a specific URL
python langchain_browser_use.py --url https://linkedin.com/jobs --query "Apply to software engineer positions"

# Run in headless mode
python langchain_browser_use.py --headless

# Use specific Gemini models
python langchain_browser_use.py --model gemini-2.0-flash-exp --planner-model gemini-1.5-pro
```

### Additional Tools

#### Resume Tailoring
Customize your resume for specific job postings:
```bash
python resume_tailor.py
```

#### Job Extraction
Extract job listings from websites:
```bash
python job_extractor.py
```

#### Hiring Cafe Scraper
Scrape jobs from Hiring Cafe:
```bash
python hiring_cafe_scraper.py
```

## Example Commands

When running `job_applicant.py`, you can give natural language instructions like:

- "Go to LinkedIn jobs and search for Python developer positions in San Francisco"
- "Apply to the first 5 job postings that don't require a cover letter"
- "Fill out the application form using my resume information"
- "Save the job descriptions to a CSV file"

## Project Structure

```
job_applicant/
├── job_applicant.py          # Main automation script
├── langchain_mcp.py          # LangChain implementation
├── langchain_browser_use.py  # Browser-use implementation
├── resume_tailor.py          # Resume customization tool
├── job_extractor.py          # Job listing extractor
├── hiring_cafe_scraper.py    # Hiring Cafe specific scraper
├── tailored_resumes/         # Generated text resumes
├── tailored_resumes_latex/   # LaTeX formatted resumes
├── tailored_resumes_pdf/     # PDF versions of resumes
└── requirements.txt          # Python dependencies
```

## How It Works

1. **Multi-Step Processing**: The tool breaks down complex tasks into manageable steps
2. **Context Awareness**: Maintains conversation history to understand multi-part instructions
3. **Tool Orchestration**: Coordinates between browser automation and AI decision-making
4. **Error Recovery**: Handles common web automation challenges gracefully

## Troubleshooting

### Browser won't open
- Ensure Playwright is properly installed: `npx playwright install chromium`
- Check if MCP server is running: `npm list -g @playwright/mcp`

### API errors
- Verify your Gemini API key is set correctly in `.env`
- Check API quota limits at [Google AI Studio](https://aistudio.google.com/)

### Connection issues
- Ensure all MCP servers are installed globally with npm
- Try restarting the script if connection times out

## Configuration

The `.mcp.json` file can be modified to add more MCP servers or change settings:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "BROWSER_NAME": "chromium",
        "HEADLESS": "false"
      }
    }
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Playwright MCP](https://github.com/playwright/mcp)
- Powered by [Google Gemini API](https://ai.google.dev/)
- Uses [LangChain](https://langchain.com/) for advanced implementations

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/sapoepsilon/job_applicant/issues)
- Check existing issues for solutions
- Ensure you've followed all installation steps

---

**Note**: This tool is for educational and personal use. Always comply with website terms of service and use responsibly.