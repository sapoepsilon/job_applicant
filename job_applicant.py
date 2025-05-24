import asyncio
import os
import sys
import pandas as pd
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import re
from urllib.parse import urlparse
from datetime import datetime
import base64

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Credential management constants
CREDENTIALS_FILE = "/Users/ismatullamansurov/Developer/job_applicant/job_credentials.csv"

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

def extract_domain(url):
    """Extract the main domain from a URL, handling various formats."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Extract just the main domain (e.g., 'example.com' from 'jobs.example.com')
        parts = domain.split('.')
        if len(parts) > 2:
            # Keep the last two parts for most domains (e.g., example.com)
            # But handle special cases like co.uk, com.au, etc.
            if parts[-2] in ['co', 'com', 'net', 'org', 'edu', 'gov']:
                domain = '.'.join(parts[-3:])
            else:
                domain = '.'.join(parts[-2:])
        
        return domain.lower()
    except:
        return None

def encode_password(password):
    """Simple encoding for password storage. NOT SECURE - for demo purposes only."""
    # In production, use proper encryption or a secure password manager
    return base64.b64encode(password.encode()).decode()

def decode_password(encoded_password):
    """Decode the encoded password."""
    return base64.b64decode(encoded_password.encode()).decode()

def initialize_credentials_file():
    """Create the credentials CSV file if it doesn't exist."""
    if not os.path.exists(CREDENTIALS_FILE):
        df = pd.DataFrame(columns=['domain', 'username', 'password', 'created_date', 'last_used'])
        df.to_csv(CREDENTIALS_FILE, index=False)
        print(f"📁 Created credentials file: {CREDENTIALS_FILE}")
        print("⚠️  SECURITY WARNING: This file contains encoded passwords. Keep it secure!")

def save_credentials(url, username, password):
    """Save new credentials for a domain."""
    domain = extract_domain(url)
    if not domain:
        print(f"⚠️  Could not extract domain from URL: {url}")
        return
    
    initialize_credentials_file()
    
    # Read existing credentials
    df = pd.read_csv(CREDENTIALS_FILE)
    
    # Check if credentials already exist for this domain
    existing = df[df['domain'] == domain]
    
    if not existing.empty:
        # Update existing credentials
        df.loc[df['domain'] == domain, 'username'] = username
        df.loc[df['domain'] == domain, 'password'] = encode_password(password)
        df.loc[df['domain'] == domain, 'last_used'] = datetime.now().isoformat()
        print(f"🔄 Updated credentials for {domain}")
    else:
        # Add new credentials
        new_row = pd.DataFrame([{
            'domain': domain,
            'username': username,
            'password': encode_password(password),
            'created_date': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat()
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        print(f"💾 Saved new credentials for {domain}")
    
    # Save to file
    df.to_csv(CREDENTIALS_FILE, index=False)

def get_credentials(url):
    """Retrieve existing credentials for a domain."""
    domain = extract_domain(url)
    if not domain:
        return None, None
    
    if not os.path.exists(CREDENTIALS_FILE):
        return None, None
    
    df = pd.read_csv(CREDENTIALS_FILE)
    
    # Look for credentials for this domain
    matching = df[df['domain'] == domain]
    
    if not matching.empty:
        # Update last_used timestamp
        df.loc[df['domain'] == domain, 'last_used'] = datetime.now().isoformat()
        df.to_csv(CREDENTIALS_FILE, index=False)
        
        # Return the credentials
        row = matching.iloc[0]
        return row['username'], decode_password(row['password'])
    
    return None, None

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
    job_title = str(job_data.get('job_title', 'Unknown'))
    company = str(job_data.get('company', 'Unknown'))
    external_url = str(job_data.get('external_url', ''))
    job_description = str(job_data.get('job_description', ''))
    
    # Check if job requires security clearance
    security_keywords = ['security clearance', 'secret clearance', 'top secret', 'ts/sci', 
                        'clearance required', 'active clearance', 'dod clearance', 
                        'government clearance', 'clearance level']
    if any(keyword in job_description.lower() for keyword in security_keywords):
        print(f"⚠️  Skipping {job_title} at {company} - requires security clearance")
        return False, "Requires security clearance"
    
    # First check if resume path is in CSV
    resume_path_raw = job_data.get('resume_pdf_path', '')
    
    # Convert to string and handle NaN/None/float cases
    if pd.isna(resume_path_raw) or resume_path_raw is None:
        resume_path = ''
    else:
        resume_path = str(resume_path_raw).strip()
    
    # If not in CSV or file doesn't exist, try to find matching resume
    if not resume_path or not os.path.exists(resume_path):
        resume_path = find_matching_resume(job_title, company)
        if not resume_path:
            print(f"No matching resume found for {job_title} at {company}")
            return False, "No matching resume found"
    
    print(f"\nApplying to: {job_title} at {company}")
    print(f"Using resume: {os.path.basename(resume_path)}")
    print(f"URL: {external_url}")
    
    # Check for existing credentials
    existing_username, existing_password = get_credentials(external_url)
    
    if existing_username and existing_password:
        print(f"🔑 Found existing credentials for {extract_domain(external_url)}")
        credential_info = f"""
EXISTING CREDENTIALS FOUND:
- Email: {existing_username}
- Password: {existing_password}
- Use these credentials to log in instead of creating a new account"""
    else:
        print(f"🆕 No existing credentials found for {extract_domain(external_url)}")
        credential_info = f"""
NO EXISTING CREDENTIALS:
- Create a new account using email: ismatulla@mansurov.dev
- Generate a secure random password (at least 12 characters with mixed case, numbers, and symbols)
- IMPORTANT: After successfully creating the account, remember the password you used so we can save it"""
    
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

{credential_info}

TASK: Apply to {job_title} Position at {company}
1. Navigate to: {external_url}

2. Complete the job application process:
   - First check if you need to log in or create an account
   - If logging in, use the existing credentials provided above
   - If creating a new account, use the email and generate a secure password
   - Fill out all required personal information fields
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
   - IMPORTANT: If you create a new account, report back the password you used in your final response

4. Handle any errors or issues:
   - If the resume upload fails, try alternative upload methods
   - If forms don't submit, take screenshots and document the issue
   - If redirected to different pages, adapt and continue the application process

5. Completion:
   - Submit the application when all required fields are filled
   - CRITICAL: After clicking submit, you MUST wait for and verify one of these:
     * A success message (e.g., "Application submitted successfully", "Thank you for applying", "Your application has been received")
     * A confirmation page or redirect to a "thank you" page
     * An email confirmation message on the page
     * Any clear indication that the application was processed
   - Take a screenshot of the confirmation/success message
   - If no confirmation appears after 10 seconds, check for:
     * Error messages that need to be addressed
     * Required fields that were missed
     * Captcha or verification steps
   - Report the final status with details about the confirmation received
   - If you created a new account, include the password in your response like: "Password used: [the_password_here]"

IMPORTANT: The task is NOT complete until you see explicit confirmation that the application was submitted. If you only see the submit button without confirmation, continue checking or retrying.

Approach this task step-by-step. When you receive confirmation of successful submission, output `Complete` followed by a description of the confirmation you received (e.g., "Complete - Received 'Thank you for applying' message")"""

    current_context = prompt
    total_token_usage = 0
    max_attempts = 10  # Prevent infinite loops
    attempt = 0
    new_password = None

    while attempt < max_attempts:
        try:
            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash-preview-04-17",
                contents=current_context,
                config=types.GenerateContentConfig(
                    system_instruction="You are an automated job application assistant with access to browser automation and terminal tools, you have access to gmail use that if the website wants you to input something from an email it sends you. Use these tools effectively to complete the assigned task. IMPORTANT: After submitting an application, you MUST wait for and verify explicit confirmation (success message, thank you page, confirmation email, etc.) before considering the task complete. When you see confirmation, output: 'Complete - [description of confirmation received]'. If you created a new account, always include the password you used in your response.",
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
                
                # Check if a new password was created
                password_match = re.search(r'[Pp]assword\s*(?:used|created|is)?:\s*([^\s\n]+)', combined_text)
                if password_match:
                    new_password = password_match.group(1)
                
                if combined_text.lower().startswith("complete"):
                    # Extract the confirmation details if provided
                    confirmation_details = "Application submitted successfully"
                    if " - " in combined_text:
                        confirmation_details = combined_text.split(" - ", 1)[1]
                    
                    print(f"✅ Application completed successfully for {job_title} at {company}")
                    print(f"   Confirmation: {confirmation_details}")
                    
                    # Save credentials if a new account was created
                    if new_password and not existing_username:
                        save_credentials(external_url, "ismatulla@mansurov.dev", new_password)
                    
                    return True, confirmation_details
                # Add debug information about what we're seeing
                print(f"🔍 Response text: {combined_text[:100]}..." if len(combined_text) > 100 else f"🔍 Response text: {combined_text}")
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
    # Initialize credentials file at startup
    initialize_credentials_file()
    
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
            # Get CSV file from command line argument or prompt user
            if len(sys.argv) > 1:
                csv_file = sys.argv[1]
            else:
                # Find all CSV files in the directory
                import glob
                csv_files = glob.glob(os.path.join(os.path.dirname(__file__), "*_jobs.csv"))
                
                if not csv_files:
                    print("❌ No job CSV files found in the project directory!")
                    print("💡 Please scrape some jobs first using the hiring_cafe_scraper.py")
                    return
                
                if len(csv_files) == 1:
                    csv_file = csv_files[0]
                    print(f"Found one CSV file: {os.path.basename(csv_file)}")
                else:
                    print("\n📁 Available job CSV files:")
                    for i, file in enumerate(csv_files, 1):
                        # Count jobs in each file
                        try:
                            temp_df = pd.read_csv(file)
                            job_count = len(temp_df)
                            # Handle NaN values in applied column
                            if 'applied' in temp_df.columns:
                                temp_df['applied'] = temp_df['applied'].fillna('').astype(str)
                                unapplied_count = len(temp_df[~temp_df['applied'].str.lower().isin(['yes', 'true', 'applied'])])
                            else:
                                unapplied_count = job_count
                            print(f"{i}. {os.path.basename(file)} ({job_count} total jobs, {unapplied_count} not yet applied)")
                        except Exception as e:
                            print(f"{i}. {os.path.basename(file)}")
                    
                    while True:
                        try:
                            choice = int(input("\nSelect CSV file number: "))
                            if 1 <= choice <= len(csv_files):
                                csv_file = csv_files[choice - 1]
                                break
                            else:
                                print("❌ Invalid selection")
                        except ValueError:
                            print("❌ Please enter a number")
            
            print(f"\n📊 Processing jobs from: {os.path.basename(csv_file)}")
            
            # Read the CSV into a DataFrame
            df = pd.read_csv(csv_file)
            
            # Add 'applied' column if it doesn't exist
            if 'applied' not in df.columns:
                df['applied'] = ''
            
            # Show summary of jobs
            total_jobs = len(df)
            # Convert applied column to string and handle NaN values
            df['applied'] = df['applied'].fillna('').astype(str)
            already_applied = len(df[df['applied'].str.lower().isin(['yes', 'true', 'applied'])])
            no_url = len(df[df['external_url'].isna() | (df['external_url'] == '')])
            
            # Count jobs requiring security clearance
            security_clearance_count = 0
            security_keywords = ['security clearance', 'secret clearance', 'top secret', 'ts/sci', 
                                'clearance required', 'active clearance', 'dod clearance', 
                                'government clearance', 'clearance level']
            for _, row in df.iterrows():
                job_desc = str(row.get('job_description', '')).lower()
                if any(keyword in job_desc for keyword in security_keywords):
                    security_clearance_count += 1
            
            to_apply = total_jobs - already_applied - no_url - security_clearance_count
            
            print(f"\n📊 Job Summary:")
            print(f"   Total jobs in CSV: {total_jobs}")
            print(f"   Already applied: {already_applied}")
            print(f"   Missing external URL: {no_url}")
            print(f"   Requires security clearance: {security_clearance_count}")
            print(f"   Ready to apply: {to_apply}")
            
            if to_apply == 0:
                print("\n✅ All jobs have been processed!")
                return
            
            # Ask for confirmation
            response = input(f"\n🚀 Ready to apply to {to_apply} jobs? (Y/n): ").strip().lower()
            if response == 'n':
                print("👋 Job application cancelled")
                return
            
            # Process each job that hasn't been applied to yet
            total_applications = 0
            successful_applications = 0
            total_retries = 0
            
            for index, row in df.iterrows():
                # Skip if already applied or no external URL
                applied_value = str(row.get('applied', '')).strip().lower()
                if applied_value in ['yes', 'true', 'applied']:
                    print(f"\nSkipping {row['job_title']} at {row['company']} - already applied")
                    continue
                    
                external_url = row.get('external_url', '')
                if pd.isna(external_url) or str(external_url).strip() == '':
                    print(f"\nSkipping {row['job_title']} at {row['company']} - no external URL")
                    df.at[index, 'applied'] = 'No external URL'
                    continue
                
                # Check for security clearance requirement
                job_description = str(row.get('job_description', ''))
                security_keywords = ['security clearance', 'secret clearance', 'top secret', 'ts/sci', 
                                    'clearance required', 'active clearance', 'dod clearance', 
                                    'government clearance', 'clearance level']
                if any(keyword in job_description.lower() for keyword in security_keywords):
                    print(f"\nSkipping {row['job_title']} at {row['company']} - requires security clearance")
                    df.at[index, 'applied'] = 'Requires security clearance'
                    df.to_csv(csv_file, index=False)
                    continue
                
                total_applications += 1
                
                # Apply to the job with retry logic
                max_retries = 3
                retry_count = 0
                success = False
                status_message = ""
                
                while retry_count < max_retries and not success:
                    if retry_count > 0:
                        print(f"\n🔄 Retry attempt {retry_count} of {max_retries} for {row['job_title']} at {row['company']}")
                        # Wait a bit longer between retries
                        await asyncio.sleep(10)
                    
                    success, status_message = await apply_to_job(row, term_session, gmail_use_session, browser_use_session)
                    
                    if not success:
                        retry_count += 1
                        total_retries += 1
                        if retry_count < max_retries:
                            print(f"⚠️  Application failed: {status_message}. Will retry...")
                            # Try to close browser before retry to clean up any stuck state
                            try:
                                await browser_use_session.call_tool("browser_close", arguments={})
                            except:
                                pass
                    else:
                        break
                
                # Update the DataFrame
                if success:
                    df.at[index, 'applied'] = 'Yes'
                    successful_applications += 1
                    print(f"✅ Successfully applied to {row['job_title']} at {row['company']}")
                else:
                    final_status = f"{status_message} (Failed after {retry_count} retries)"
                    df.at[index, 'applied'] = final_status
                    print(f"❌ Failed to apply to {row['job_title']} at {row['company']} after {retry_count} retries")
                
                # Save the updated CSV after each application
                df.to_csv(csv_file, index=False)
                print(f"\nUpdated CSV with application status for {row['job_title']} at {row['company']}")
                
                # Close the browser after each application to free resources
                try:
                    await browser_use_session.call_tool("browser_close", arguments={})
                    print("Browser closed successfully")
                except Exception as e:
                    print(f"Warning: Failed to close browser: {e}")
                
                # Add a small delay between applications to avoid being detected as a bot
                await asyncio.sleep(5)
            
            print(f"\n\n=== JOB APPLICATION SUMMARY ===")
            print(f"Total jobs processed: {total_applications}")
            print(f"Successful applications: {successful_applications}")
            print(f"Failed applications: {total_applications - successful_applications}")
            print(f"Total retry attempts: {total_retries}")
            print(f"CSV file updated with application statuses: {csv_file}")
            
            return True

# Start the asyncio event loop and run the main function
if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python job_applicant.py [csv_file_path]")
        print("Example: python job_applicant.py ios_developer_jobs.csv")
        sys.exit(1)
    
    asyncio.run(run())