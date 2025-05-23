# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a browser automation tool that combines Playwright Model Context Protocol (MCP) with Google's Gemini API to execute natural language instructions for web automation tasks. The project includes three main scripts, each demonstrating different approaches to browser automation:

1. `job_applicant.py`: Main script that creates an intelligent agent for job application automation using Playwright MCP and Gemini API.
2. `langchain_mcp.py`: Alternative implementation using LangChain and multiple MCP servers.
3. `langchain_browser_use.py`: Implementation using the browser-use library with Gemini models.

## Commands

### Setup and Run

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install required MCP packages globally
npm install -g @playwright/mcp
npm install -g @wonderwhy-er/desktop-commander

# Run the main job application script
python job_applicant.py

# Run alternative implementations
python langchain_mcp.py
python langchain_browser_use.py
```

### Script-Specific Run Options

For `langchain_browser_use.py`, several command-line options are available:

```bash
# Run with a specific starting URL and query
python langchain_browser_use.py --url https://example.com --query "Find information about X"

# Run in headless mode
python langchain_browser_use.py --headless

# Use specific Gemini models
python langchain_browser_use.py --model gemini-2.5-flash-preview-04-17 --planner-model gemini-2.5-flash-preview-04-17
```

### Environment Setup

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_api_key_here
```

## Architecture

### Key Components

1. **Multiple MCP Servers**:
   - Playwright MCP (`@playwright/mcp@latest`): Handles browser automation
   - Terminal Controller MCP (`@wonderwhy-er/desktop-commander`): Handles terminal operations
   - Additional servers in `langchain_mcp.py`: Context7, PostgreSQL, iTerm, Filesystem, Todoist

2. **Multi-Step Prompt Processing**:
   - First API call creates focused instructions for the next step
   - Second API call executes browser automation using the instruction
   - Context maintains conversation history with function calls and results

3. **Different Implementation Approaches**:
   - Direct MCP client in `job_applicant.py`
   - LangChain with ReAct agent in `langchain_mcp.py`
   - Browser-use agent with planning in `langchain_browser_use.py`

4. **Tool Mapping**:
   - Tools from MCP servers are aggregated
   - Each tool is mapped to its respective session for proper execution

## Development Approach

### Function Call Flow
The main script maintains a loop for complex automation tasks:
```
User Prompt → First Gemini Call (instruction creation) → Second Gemini Call (execution) → Tool Execution → Result → Context Update → Repeat
```

### Context Management
- Maintains `function_calls` and `function_args` lists
- Tracks current step number
- Accumulates historic text responses
- Updates context with task prompt and latest results

### Debugging
- For browser automation issues, check browser console logs and ensure the browser is properly initialized
- For MCP server connection issues, verify npm packages are correctly installed
- For Gemini API errors, check the API key is correctly set in the `.env` file
- Use the `--headless=false` option with `langchain_browser_use.py` to see browser actions visually
- The browser-use agent creates GIFs of browser sessions for later review

## Key Files
- `job_applicant.py`: Main script with Gemini integration and MCP client setup
- `langchain_mcp.py`: Alternative implementation using LangChain and multiple MCP servers
- `langchain_browser_use.py`: Implementation using browser-use library with planning capabilities
- `requirements.txt`: All required Python dependencies with version specifications