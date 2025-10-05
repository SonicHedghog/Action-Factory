"""
Default tools for the Action Factory system
"""
from registry import register_tool
import os
import json
import math
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

def google_search(query: str) -> str:
    """
    Search Google for information about a query.
    
    Args:
        query: The search query string
        
    Returns:
        Search results or instructions for setting up API access
    """
    # Check if API keys are available
    google_api_key = os.getenv('GOOGLE_API_KEY')
    google_cse_id = os.getenv('GOOGLE_CSE_ID')
    
    if not google_api_key or not google_cse_id:
        return f"""Google Search for: "{query}"

⚠️  Google Search API not configured. To enable real Google search:

1. Get a Google API Key:
   - Go to https://console.developers.google.com/
   - Create a project and enable Custom Search API
   - Create credentials (API Key)

2. Set up Custom Search Engine:
   - Go to https://cse.google.com/
   - Create a custom search engine
   - Get your Search Engine ID

3. Set environment variables:
   export GOOGLE_API_KEY="your_api_key_here"
   export GOOGLE_CSE_ID="your_search_engine_id_here"

Query: {query}
Status: API keys not configured - showing setup instructions instead"""
    
    try:
        # Try to use LangChain's Google search if keys are available
        from langchain_community.tools import GoogleSearchRun
        from langchain_community.utilities import GoogleSearchAPIWrapper
        
        search = GoogleSearchAPIWrapper(
            google_api_key=google_api_key,
            google_cse_id=google_cse_id
        )
        google_search_tool = GoogleSearchRun(api_wrapper=search)
        return google_search_tool.run(query)
        
    except Exception as e:
        return f"Error performing Google search: {str(e)}\n\nQuery: {query}"

def calculate_math(expression: str) -> str:
    """
    Safely evaluate mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 3 * 4")
        
    Returns:
        Result of the calculation or error message
    """
    try:
        # Only allow safe mathematical operations
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
        
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

def current_time(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get the current date and time.
    
    Args:
        format_str: Format string for the datetime (default: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        Current date and time as formatted string
    """
    try:
        now = datetime.now()
        return now.strftime(format_str)
    except Exception as e:
        return f"Error getting current time: {str(e)}"

def generate_random_number(min_val: int = 1, max_val: int = 100) -> str:
    """
    Generate a random number within a specified range.
    
    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        
    Returns:
        Random number as string
    """
    try:
        number = random.randint(min_val, max_val)
        return f"Random number between {min_val} and {max_val}: {number}"
    except Exception as e:
        return f"Error generating random number: {str(e)}"

def text_analyzer(text: str) -> str:
    """
    Analyze text and provide basic statistics.
    
    Args:
        text: Text to analyze
        
    Returns:
        Analysis results including word count, character count, etc.
    """
    try:
        words = text.split()
        sentences = text.split('.')
        paragraphs = text.split('\n\n')
        
        analysis = {
            "character_count": len(text),
            "character_count_no_spaces": len(text.replace(' ', '')),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len([p for p in paragraphs if p.strip()]),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "longest_word": max(words, key=len) if words else "",
            "shortest_word": min(words, key=len) if words else ""
        }
        
        result = "Text Analysis Results:\n"
        for key, value in analysis.items():
            result += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        return result
    except Exception as e:
        return f"Error analyzing text: {str(e)}"

def json_formatter(data: str) -> str:
    """
    Format and validate JSON data.
    
    Args:
        data: JSON string to format
        
    Returns:
        Formatted JSON or error message
    """
    try:
        # Try to parse and reformat the JSON
        parsed = json.loads(data)
        formatted = json.dumps(parsed, indent=2, sort_keys=True)
        return f"Formatted JSON:\n{formatted}"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {str(e)}"
    except Exception as e:
        return f"Error formatting JSON: {str(e)}"

def password_generator(length: int = 12, include_symbols: bool = True) -> str:
    """
    Generate a secure random password.
    
    Args:
        length: Length of the password (default: 12)
        include_symbols: Whether to include symbols (default: True)
        
    Returns:
        Generated password
    """
    try:
        import string
        
        characters = string.ascii_letters + string.digits
        if include_symbols:
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        password = ''.join(random.choice(characters) for _ in range(length))
        return f"Generated password: {password}"
    except Exception as e:
        return f"Error generating password: {str(e)}"

def url_validator(url: str) -> str:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        Validation result and analysis
    """
    try:
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        
        is_valid = bool(parsed.scheme and parsed.netloc)
        
        analysis = {
            "is_valid": is_valid,
            "scheme": parsed.scheme,
            "domain": parsed.netloc,
            "path": parsed.path,
            "query": parsed.query,
            "fragment": parsed.fragment
        }
        
        result = f"URL Validation for: {url}\n"
        result += f"Valid: {is_valid}\n"
        if is_valid:
            result += f"Scheme: {analysis['scheme']}\n"
            result += f"Domain: {analysis['domain']}\n"
            if analysis['path']:
                result += f"Path: {analysis['path']}\n"
            if analysis['query']:
                result += f"Query: {analysis['query']}\n"
            if analysis['fragment']:
                result += f"Fragment: {analysis['fragment']}\n"
        
        return result
    except Exception as e:
        return f"Error validating URL: {str(e)}"

def init_default_tools():
    """Initialize default tools in the registry"""
    tools_to_register = [
        ("google_search", google_search, "Search Google for information about a query"),
        ("calculate_math", calculate_math, "Safely evaluate mathematical expressions"),
        ("current_time", current_time, "Get the current date and time with optional formatting"),
        ("generate_random_number", generate_random_number, "Generate a random number within a specified range"),
        ("text_analyzer", text_analyzer, "Analyze text and provide statistics like word count, character count, etc."),
        ("json_formatter", json_formatter, "Format and validate JSON data"),
        ("password_generator", password_generator, "Generate a secure random password with customizable options"),
        ("url_validator", url_validator, "Validate if a URL is properly formatted and analyze its components")
    ]
    
    for name, func, description in tools_to_register:
        register_tool(name, func, description)
    
    print(f"✓ Default tools registered: {', '.join([name for name, _, _ in tools_to_register])}")