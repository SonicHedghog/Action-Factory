import os
from typing import List, Any
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from registry import tool_registry
from planner import intelligent_plan_and_execute, get_available_tools_description

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

# Model configuration
model = os.getenv('GOOGLE_MODEL', 'gemini-2.5-pro')  # Default to gemini-2.5-pro if not specified

llm = ChatGoogleGenerativeAI(model=model, google_api_key=gemini_api_key)

# Agent LLM for final response generation
agent_llm = ChatGoogleGenerativeAI(
    model=model, 
    temperature=0.7, 
    google_api_key=gemini_api_key
)

def build_agent():
    """Build a LangChain agent with current tools."""
    tools = list(tool_registry.values())
    if not tools:
        return None
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent

def generate_intelligent_response(query: str, execution_results: List[Any]) -> str:
    """
    Generate an intelligent response based on the query and execution results.
    """
    tools_info = get_available_tools_description()
    
    response_prompt = f"""
You are an AI assistant that has just executed a plan to handle a user's request.

User Query: "{query}"

Available Tools:
{tools_info}

Execution Results:
{execution_results}

Please provide a helpful, concise response to the user that:
1. Acknowledges their request
2. Summarizes what was accomplished
3. Presents any results or findings
4. Offers next steps if appropriate
5. Is conversational and user-friendly

If tools were created, mention that new capabilities were added.
If existing tools were used, mention how they helped.
If there were errors, explain them in a user-friendly way.
"""
    
    try:
        response = agent_llm([HumanMessage(content=response_prompt)])
        content = response.content
        if isinstance(content, str):
            return content
        else:
            return str(content)
    except Exception as e:
        # Fallback response
        results_summary = f"Executed plan with {len(execution_results)} steps."
        if execution_results:
            results_summary += f" Results: {execution_results}"
        return f"I've processed your request: '{query}'. {results_summary}"

def process_query_intelligently(query: str) -> str:
    """
    Process a user query using intelligent planning and execution.
    """
    print(f"\n{'='*60}")
    print(f"🎯 Processing: {query}")
    print(f"{'='*60}")
    
    # Use intelligent planning to handle the query
    execution_results = intelligent_plan_and_execute(query)
    
    # Generate a natural language response
    response = generate_intelligent_response(query, execution_results)
    
    return response

def run_agent_loop():
    """
    Main agent loop with intelligent planning and fallback to LangChain agent.
    """
    print("🤖 AI Agent with Intelligent Planning ready!")
    print("   - I can analyze your requests and create tools as needed")
    print("   - I'll use existing tools when possible")
    print("   - I'll create new tools when necessary")
    print("   - Type 'help' for more information")
    print("   - Press Ctrl+C to quit")
    print(f"\n📊 Initial state: {len(tool_registry)} tools available")
    
    while True:
        try:
            query = input("\n🎯 You> ").strip()
            if not query:
                continue
                
            if query.lower() in ['help', '?']:
                print_help()
                continue
                
            if query.lower() in ['status', 'tools']:
                print_status()
                continue
                
            if query.lower() in ['reset']:
                from registry import reset_registry
                reset_registry()
                print("🔄 Registry reset. All tools cleared.")
                continue
            
            # Process the query using intelligent planning
            response = process_query_intelligently(query)
            
            print(f"\n🤖 Assistant: {response}")
            
            # Show updated tool count
            tool_count = len(tool_registry)
            print(f"\n📊 Status: {tool_count} tools available")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using the AI Agent.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.")

def print_help():
    """Print help information."""
    print("""
🔧 AI Agent Help:

Commands:
  help, ?     - Show this help message
  status      - Show available tools and system status
  tools       - List all available tools
  reset       - Clear all tools and start fresh

How it works:
1. I analyze your request to understand what you need
2. If existing tools can help, I'll use them
3. If new tools are needed, I'll create them automatically
4. I'll execute a plan to accomplish your goal

Examples:
  "Search for information about Python"
  "Calculate the fibonacci sequence"
  "Create a tool to convert temperature"
  "Help me organize my tasks"

I can handle a wide variety of requests and will adapt by creating
the tools needed to help you accomplish your goals.
""")

def print_status():
    """Print current system status."""
    tool_count = len(tool_registry)
    print(f"\n📊 System Status:")
    print(f"   Tools available: {tool_count}")
    
    if tool_count > 0:
        print(f"\n🛠️  Available Tools:")
        for name, tool in tool_registry.items():
            description = getattr(tool, 'description', 'No description')
            print(f"   - {name}: {description}")
    else:
        print("   No tools currently registered.")
    
    print(f"\n🔧 AI Features:")
    print(f"   ✓ Intelligent request analysis")
    print(f"   ✓ Automatic tool creation")
    print(f"   ✓ Tool testing and validation")
    print(f"   ✓ Peer-to-peer tool sharing")

# Legacy compatibility function
def run_agent_with_fallback():
    """
    Legacy function that can fall back to LangChain agent if needed.
    """
    agent = build_agent()
    if agent and len(tool_registry) > 0:
        return agent
    else:
        print("No tools available for LangChain agent. Using intelligent planning only.")
        return None