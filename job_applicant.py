import asyncio
import os
import sys
import pandas as pd
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import re

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Create server parameters for stdio connection
browser_use_params = StdioServerParameters(
    command="npx",  # Executable
    args=["-y", "@playwright/mcp@latest","--no-sandbox","--user-data-dir=/Users/ismatullamansurov/Library/Caches/ms-playwright/chromium-1148"],
    env=None,
)

terminal_params = StdioServerParameters(
    command="npx",  # Executable
    args=["-y", "@wonderwhy-er/desktop-commander@latest"],  # Terminal controller MCP
    env=None,
)

# browser_use_params = StdioServerParameters(
#     command="uvx",  # Executable
#     args=["mcp-server-browser-use@latest"],  # Terminal controller MCP
#     env={
#         "MCP_LLM_GOOGLE_API_KEY": os.getenv("GEMINI_API_KEY"),
#         "MCP_LLM_PROVIDER": "google",
#         "MCP_LLM_MODEL_NAME": "gemini-2.5-flash-preview-04-17",
#         "MCP_BROWSER_HEADLESS": "false",
#         "MCP_AGENT_TOOL_USE_VISION": "true",
#         "MCP_AVAILABLE_PATHS": "/Users/ismatullamansurov/Developer",
#     },
# )

gmail_use_params = StdioServerParameters(
    command="npx",  # Executable
    args=["-y", "@smithery/cli@latest", "run", "@gongrzhe/server-gmail-autoauth-mcp"],  #gmail 
    env=None,
)

def find_matching_resume(job_title, company, resume_dir="/Users/ismatullamansurov/Developer/job_applicant/tailored_resumes_pdf"):
    """Find the matching tailored resume PDF for a job."""
    # Clean job title and company name for matching
    clean_title = re.sub(r'[^\w\s]', '', job_title).strip()
    clean_company = re.sub(r'[^\w\s]', '', company).strip()
    
    # List all PDFs in the directory
    pdf_files = [f for f in os.listdir(resume_dir) if f.endswith('.pdf')]
    
    # Try to find exact match first
    for pdf in pdf_files:
        if clean_company.lower() in pdf.lower() and any(word.lower() in pdf.lower() for word in clean_title.split()):
            return os.path.join(resume_dir, pdf)
    
    # If no exact match, try company name only
    for pdf in pdf_files:
        if clean_company.lower() in pdf.lower():
            return os.path.join(resume_dir, pdf)
    
    # Return None if no match found
    return None

async def apply_to_job(job_data, term_session, gmail_use_session, browser_use_session):
    """Apply to a single job using the browser automation."""
    job_title = job_data['job_title']
    company = job_data['company']
    external_url = job_data['external_url']
    
    # First check if resume path is in CSV
    resume_path = job_data.get('resume_pdf_path', '').strip()
    
    # If not in CSV or file doesn't exist, try to find matching resume
    if not resume_path or not os.path.exists(resume_path):
        resume_path = find_matching_resume(job_title, company)
        if not resume_path:
            print(f"No matching resume found for {job_title} at {company}")
            return False, "No matching resume found"
    
    print(f"\nApplying to: {job_title} at {company}")
    print(f"Using resume: {os.path.basename(resume_path)}")
    print(f"URL: {external_url}")
    
    prompt = f"""You are an automated job application assistant with two integrated tools: a browser automation system and a terminal access system. 

CAPABILITIES:
- Browser automation: Navigate websites, fill forms, upload files, interact with web elements
- Terminal access: Create, edit, and manage files on the local system

PERSONAL INFORMATION:
- Name: Ismatulla Mansurov
- Email: ismatulla@mansurov.dev
- Race/Ethnicity: White
- phone: 8016350784
- LinkedIn: https://www.linkedin.com/in/ismatulla-mansurov/
- GitHub: https://github.com/sapoepsilon
- I am not disabled
- I am not a veteran
- Location: Salt Lake City, Utah, United States or any other variation of it. Sometimes the field has auto suggest just choose the one that is closest to Salt Lake City, Utah, United States
- I am willing to relocate
- preferred name: Izzy
- Resume Location: '{resume_path}'

TASK: Apply to {job_title} Position at {company}
1. Navigate to: {external_url}

2. Complete the job application process:
   - Fill out all required personal information fields
   - If need to create an account use ismatulla@mansurov.dev and use any random password
   - Upload the specified resume file
   - Go one by one and try to fill out the form
   - If the input has been filled out correctly, move to the next input
   - if the input has values already just go to the next input
   - Answer any application questions using the provided personal information
   - Handle race/ethnicity questions by selecting "White"
   - Use professional, enthusiastic responses for any text fields
   - I would need a sponsorship in the future, but for now I am authorized to work in the US
   - I am on OPT
   - I am authorized to work in the US

3. Important Application Guidelines:
   - Take screenshots at key steps to document progress
   - If asked about authorization to work, answer "Yes" (assume legal work authorization)
   - For salary expectations, use market-rate responses or "Negotiable"
   - For "Why do you want to work here" type questions, focus on the company's scale, technology impact, and innovation
   - Be thorough but efficient - complete all required fields
   - Ignore the steps that are not required if you don't have info for those

4. Handle any errors or issues:
   - If the resume upload fails, try alternative upload methods
   - If forms don't submit, take screenshots and document the issue
   - If redirected to different pages, adapt and continue the application process

5. Completion:
   - Submit the application when all required fields are filled
   - If you don't see the message "Application submitted successfully" or something similar, take screenshots and document the issue
   - Report the final status (submitted successfully, encountered errors, etc.)
   - Important: ** Make sure you get a feedback from the website that the application was submitted successfully** Without that the task is not completed.

Approach this task step-by-step, handling each part of the application process methodically. if you are done output `Complete` only and nothing else if not output the next steps
Our main goal is to complete the application process and get a feedback from the website that the application was submitted successfully. We want to do this fast if you can respond to multiple steps at once do so"""

    current_context = prompt
    total_token_usage = 0
    max_attempts = 10  # Prevent infinite loops
    attempt = 0

    while attempt < max_attempts:
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash-preview-04-17",
                contents=current_context,
                config=types.GenerateContentConfig(
                    system_instruction="You are an automated job application assistant with access to browser automation and terminal tools, you have access to gmail use that if the website wants you to input something from an email it sends you. Use these tools effectively to complete the assigned task. When you are done with the task output: Complete and little summary of the task.",
                    temperature=0.2,
                    tools=[browser_use_session, term_session, gmail_use_session],
                ),
            )
            
            if not response or not hasattr(response, 'usage_metadata'):
                raise ValueError("Invalid response from API")
                
            total_token_usage += response.usage_metadata.total_token_count
            
            # Safely get text from parts[0] and parts[1] if it exists
            part0_text = response.candidates[0].content.parts[0].text if response.candidates[0].content.parts[0].text else ""
            part1_text = response.candidates[0].content.parts[1].text if len(response.candidates[0].content.parts) > 1 and response.candidates[0].content.parts[1].text else ""
            
            if part0_text or part1_text:
                combined_text = part0_text or part1_text
                if combined_text == "Complete" or combined_text == "complete":
                    print(f"Application completed successfully for {job_title} at {company}")
                    return True, "Application submitted successfully"
                current_context += "\n Looks like we need to do more steps, last automatic function call result: " + response.automatic_function_calling_history[-1].parts[0].function_response.response['result'].content[0].text
            else:
                print("No text in response")
                print("function output dictionary: ",response.automatic_function_calling_history[-1].parts[0].function_response.response)
                current_context += "\n Looks like we need to do more steps, last automatic function call result: " + response.automatic_function_calling_history[-1].parts[0].function_response.response['result'].content[0].text
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return False, f"Error: {str(e)}"
            
        attempt += 1

    print(f"\nTotal tokens used for this application: {total_token_usage}")
    return False, "Maximum attempts reached"

async def run():
    # Connect to both MCP servers concurrently
    async with stdio_client(terminal_params) as (term_read, term_write), \
               stdio_client(gmail_use_params) as (gmail_use_read, gmail_use_write), \
               stdio_client(browser_use_params) as (browser_use_read, browser_use_write):
        
        async with ClientSession(term_read, term_write) as term_session, \
                   ClientSession(gmail_use_read, gmail_use_write) as gmail_use_session, \
                   ClientSession(browser_use_read, browser_use_write) as browser_use_session:
            
            # prompt = """Navigate to amazon.com and find 5 wireless earbuds and write them to a file as a csv with title, price, and link."""                
            await term_session.initialize()
            await gmail_use_session.initialize()
            await browser_use_session.initialize()
            
            term_tools = await term_session.list_tools()
            gmail_use_tools = await gmail_use_session.list_tools()
            browser_use_tools = await browser_use_session.list_tools()
            
            tool_session_map = {}
            all_tools = []
            
            for tool in term_tools.tools:
                tool_session_map[tool.name] = term_session
                all_tools.append(tool)
            
            for tool in browser_use_tools.tools:
                tool_session_map[tool.name] = browser_use_session
                all_tools.append(tool)
            
            for tool in gmail_use_tools.tools:
                tool_session_map[tool.name] = gmail_use_session
                all_tools.append(tool)
            
            tools = [
                types.Tool(
                    function_declarations=[
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                k: v
                                for k, v in tool.inputSchema.items()
                                if k not in ["additionalProperties", "$schema"]
                            },
                        }
                    ]
                )
                for tool in all_tools
            ]
            # Get CSV file from command line argument or use default
            if len(sys.argv) > 1:
                csv_file = sys.argv[1]
            else:
                csv_file = "/Users/ismatullamansurov/Developer/job_applicant/ios_developer_jobs.csv"
            
            print(f"Processing jobs from: {csv_file}")
            
            # Read the CSV into a DataFrame
            df = pd.read_csv(csv_file)
            
            # Add 'applied' column if it doesn't exist
            if 'applied' not in df.columns:
                df['applied'] = ''
            
            # Process each job that hasn't been applied to yet
            total_applications = 0
            successful_applications = 0
            
            for index, row in df.iterrows():
                # Skip if already applied or no external URL
                if pd.notna(row.get('applied')) and row['applied'].lower() in ['yes', 'true', 'applied']:
                    print(f"\nSkipping {row['job_title']} at {row['company']} - already applied")
                    continue
                    
                if pd.isna(row.get('external_url')) or not row['external_url'].strip():
                    print(f"\nSkipping {row['job_title']} at {row['company']} - no external URL")
                    df.at[index, 'applied'] = 'No external URL'
                    continue
                
                total_applications += 1
                
                # Apply to the job
                success, status_message = await apply_to_job(row, term_session, gmail_use_session, browser_use_session)
                
                # Update the DataFrame
                if success:
                    df.at[index, 'applied'] = 'Yes'
                    successful_applications += 1
                else:
                    df.at[index, 'applied'] = status_message
                
                # Save the updated CSV after each application
                df.to_csv(csv_file, index=False)
                print(f"\nUpdated CSV with application status for {row['job_title']} at {row['company']}")
                
                # Close the browser after each application to free resources
                try:
                    close_result = await browser_use_session.call_tool("browser_close", arguments={})
                    print("Browser closed successfully")
                except Exception as e:
                    print(f"Warning: Failed to close browser: {e}")
                
                # Add a small delay between applications to avoid being detected as a bot
                await asyncio.sleep(5)
            
            print(f"\n\n=== JOB APPLICATION SUMMARY ===")
            print(f"Total jobs processed: {total_applications}")
            print(f"Successful applications: {successful_applications}")
            print(f"Failed applications: {total_applications - successful_applications}")
            print(f"CSV file updated with application statuses: {csv_file}")
            
            return True

# Start the asyncio event loop and run the main function
if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python job_applicant.py [csv_file_path]")
        print("Example: python job_applicant.py ios_developer_jobs.csv")
        sys.exit(1)
    
    asyncio.run(run())