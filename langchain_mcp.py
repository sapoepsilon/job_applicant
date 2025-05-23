import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Get the Gemini API key from the environment variable
api_key = os.environ.get("GEMINI_API_KEY")

# Create Gemini instance LLM class
model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    temperature=0.7,
    max_retries=2,
    google_api_key=api_key,
)


async def main():
    client = MultiServerMCPClient(
        {
           "context7": {
			"command": "npx",
			"args": [
				"-y",
				"@upstash/context7-mcp@latest"
			],
            "transport": "stdio" 
		},
		"postgresql": {
			"command": "npx",
			"args": [
				"-y",
				"@modelcontextprotocol/server-postgres",
				"postgresql://postgres:postgres@127.0.0.1:54322/postgres"
			],
			"env": {},
            "transport": "stdio" 
		},
		"iterm-mcp": {
			"command": "npx",
			"args": [
				"iterm-mcp"
			],
            "transport": "stdio" 
		},
		"filesystem": {
			"command": "npx",
			"args": [
				"-y",
				"@modelcontextprotocol/server-filesystem",
				"/Users/ismatullamansurov/Developer",
				"/Users/ismatullamansurov/Documents",
				"/Users/ismatullamansurov/Downloads"
			],
            "transport": "stdio" 
		},
		"desktop-commander": {
			"command": "npx",
			"args": [
				"@wonderwhy-er/desktop-commander@latest"
			],
            "transport": "stdio" 
		},
		"todoist": {
			"command": "npx",
			"args": ["-y", "@abhiz123/todoist-mcp-server"],
			"env": {
				"TODOIST_API_TOKEN": "cfe0c7a0e03dd40618dbe3053b868f383918dedd"
			},
            "transport": "stdio" 
		},
        "playwright": {
            "command": "npx",
            "args": [
                "-y",
                "@playwright/mcp@latest"
            ],
            "transport": "stdio"
        }
          
        }
    )
    
    # Option 1: Get all tools at once
    tools = await client.get_tools()
    
    # Option 2: Use with session for a specific server
    # async with client.session("airbnb") as session:
    #     tools = await load_mcp_tools(session)
    
    # Create ReAct Agent with MCP servers
    graph = create_react_agent(model, tools)

    # Initialize conversation history using simple tuples
    inputs = {"messages": []}

    print("Agent is ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting chat.")
            break

        # Append user message to history
        inputs["messages"].append(("user", user_input))

        # call our graph with streaming to see the steps
        async for state in graph.astream(inputs, stream_mode="values"):
            last_message = state["messages"][-1]
            last_message.pretty_print()

            # update the inputs with the agent's response
            inputs["messages"] = state["messages"]


if __name__ == "__main__":
    asyncio.run(main())