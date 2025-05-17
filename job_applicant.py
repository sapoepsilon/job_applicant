import asyncio
import os
from datetime import datetime
from google import genai
from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

server_params = StdioServerParameters(
    command="npx",
    args=["@playwright/mcp@latest", "--no-sandbox"],
    env=None,
)

# Define a system prompt to guide the model in using browser tools
SYSTEM_PROMPT = """You are a helpful assistant that can interact with web browsers using Playwright.
You have access to various browser automation tools such as navigate, click, fill, get_page_content, etc.

When asked to search for something on Google or other websites:
1. First navigate to the website using the 'browser_navigate' tool
2. Find and fill the search box using 'browser_type' or 'browser_fill' tool
3. Submit the search (either by clicking a button or pressing Enter)
4. Get the page content using 'browser_get_page_content' tool
5. Extract and provide the relevant information from the search results

Always provide helpful and informative responses based on the web content you retrieve."""

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP session
            await session.initialize()
            
            # Get MCP tools and convert to Gemini function declarations
            mcp_tools = await session.list_tools()
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
                for tool in mcp_tools.tools
            ]
            
            # Create a chat session with the configured tools
            config = types.GenerateContentConfig(
                temperature=0,
                tools=tools,
            )
            
            # Initialize conversation history with system prompt
            conversation = [
                types.Content(role="user", parts=[types.Part(text=SYSTEM_PROMPT)]),
                types.Content(role="model", parts=[types.Part(text="I understand. I can help you interact with websites using browser automation tools.")]),
            ]
            
            print("Welcome to the Playwright automation assistant.")
            print("Type 'exit' to quit the program.")
            
            while True:
                # Get user prompt from terminal
                user_prompt = input("\nEnter your prompt: ")
                
                if user_prompt.lower() == 'exit':
                    print("Exiting program...")
                    break
                
                # Add user message to conversation
                conversation.append(types.Content(role="user", parts=[types.Part(text=user_prompt)]))
                
                # Get response from Gemini
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=conversation,
                    config=config,
                )
                
                # Process the response - handle multiple function calls if needed
                max_iterations = 10  # Prevent infinite loops
                iteration = 0
                
                while iteration < max_iterations:
                    iteration += 1
                    
                    # Check if the response contains a function call
                    has_function_call = False
                    function_call = None
                    text_content = ""
                    
                    # Check all parts of the response
                    if response.candidates and response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                has_function_call = True
                                function_call = part.function_call
                            elif hasattr(part, 'text'):
                                text_content += part.text
                    
                    if has_function_call and function_call:
                        print(f"\nExecuting function: {function_call.name}")
                        print(f"With parameters: {json.dumps(function_call.args, indent=2)}")
                        
                        try:
                            # Execute the function via MCP
                            result = await session.call_tool(
                                function_call.name, arguments=function_call.args
                            )
                            
                            # Extract the result text
                            result_text = ""
                            if result.content:
                                for content_part in result.content:
                                    if hasattr(content_part, 'text'):
                                        result_text += content_part.text
                            
                            # Print the result
                            print("\nFunction result:")
                            print(result_text[:500] + "..." if len(result_text) > 500 else result_text)
                            
                            # Add the function call to the conversation
                            conversation.append(types.Content(
                                role="model", 
                                parts=[types.Part(function_call=function_call)]
                            ))
                            
                            # Add the function result to the conversation
                            function_response_part = types.Part.from_function_response(
                                name=function_call.name,
                                response={"result": result_text},
                            )
                            conversation.append(types.Content(
                                role="user", 
                                parts=[function_response_part]
                            ))
                            
                            # Get next response from Gemini with the function result
                            response = client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents=conversation,
                                config=config,
                            )
                        
                        except Exception as e:
                            print(f"\nError executing function: {e}")
                            # Add error to conversation
                            error_response_part = types.Part.from_function_response(
                                name=function_call.name,
                                response={"error": str(e)},
                            )
                            conversation.append(types.Content(
                                role="user", 
                                parts=[error_response_part]
                            ))
                            
                            # Get response after error
                            response = client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents=conversation,
                                config=config,
                            )
                    
                    else:
                        # If no function call, print any text content
                        if text_content:
                            print("\nAssistant response:")
                            print(text_content)
                            
                            # Add the text response to the conversation
                            conversation.append(types.Content(
                                role="model",
                                parts=[types.Part(text=text_content)]
                            ))
                        else:
                            # If the response has text attribute, use it
                            if hasattr(response, 'text') and response.text:
                                print("\nAssistant response:")
                                print(response.text)
                                
                                # Add the response to the conversation
                                conversation.append(types.Content(
                                    role="model",
                                    parts=[types.Part(text=response.text)]
                                ))
                        
                        # Break the loop as there's no more function calls
                        break

# Run the async function
if __name__ == "__main__":
    asyncio.run(run())