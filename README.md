# Playwright MCP with Gemini Function Calling

This project demonstrates how to use the Playwright Model Context Protocol (MCP) with Google's Gemini API for browser automation through natural language instructions.

## Overview

The application creates an interactive terminal interface where you can enter natural language prompts. Gemini processes these prompts and may choose to:

1. Respond directly with text
2. Call Playwright functions to automate browser actions

The script maintains conversation history, allowing for multi-turn interactions and complex automation tasks.

## Features

- **Browser Automation**: Control web browsers using natural language
- **Conversation Context**: Maintain history for multi-step tasks
- **Function Calling**: Gemini can call Playwright functions when needed
- **Interactive Interface**: Enter prompts directly in the terminal

## Requirements

- Python 3.9+
- Node.js (for running the Playwright MCP server)
- Google Gemini API key

## Installation

1. Clone this repository
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install Playwright MCP:
   ```
   npm install -g @playwright/mcp
   ```
4. Set up your Gemini API key in a `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

Run the script:
```
python job_applicant.py
```

You'll be presented with an interactive prompt where you can enter natural language instructions for browser automation.

### Example Commands

- "Navigate to google.com"
- "Search for 'weather in London'"
- "Fill out the contact form on example.com with my information"
- "Take a screenshot of the current page"
- "Click the login button and enter my credentials"

Type 'exit' to quit the program.

## How It Works

1. **Setup**: The script initializes a connection to the Playwright MCP server
2. **Tool Discovery**: It retrieves available Playwright functions and converts them to Gemini function declarations
3. **Conversation Loop**: It enters a loop where:
   - You enter a natural language prompt
   - Gemini processes the prompt and conversation history
   - If Gemini decides to use a function, it returns a function call
   - The script executes the function through Playwright
   - The result is fed back to Gemini
   - Gemini provides a final response

## Function Calling Flow

```
User Prompt → Gemini → Function Call → Playwright MCP → Browser Action → Result → Gemini → Final Response
```

## Advanced Usage

For more complex automation tasks, you can chain multiple commands in a conversation:

1. "Navigate to mail.google.com"
2. "Log in with my credentials"
3. "Find emails from example@example.com"
4. "Download the attachments"

The script maintains conversation context, so Gemini understands the sequence of actions.

## Troubleshooting

- If the Playwright MCP server fails to start, ensure you have Node.js installed and try reinstalling the MCP package
- If Gemini doesn't use function calling when expected, try being more specific in your prompts
- Check that your Gemini API key is correctly set in the .env file

## License

MIT
