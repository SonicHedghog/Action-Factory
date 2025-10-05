import textwrap
import os
from typing import Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0, google_api_key=gemini_api_key)

def generate_tool_code(request: str, suggested_name: Optional[str] = None) -> str:
    """
    Generate Python function code for a tool based on the request.
    
    Args:
        request: Description of what the tool should do
        suggested_name: Optional suggested function name
    
    Returns:
        Generated Python function code as a string
    """
    name_hint = f"\n- Use the function name: {suggested_name}" if suggested_name else ""
    
    prompt = f"""
Write a Python function that fulfills this request: "{request}"

Requirements:
- Output exactly one top-level function definition (def ...)
- Use only standard library modules (import statements allowed)
- Include comprehensive type hints and a detailed docstring
- Make the function name descriptive and lowercase with underscores{name_hint}
- Handle edge cases and errors gracefully
- Include parameter validation where appropriate
- Return meaningful results or raise appropriate exceptions
- Do not include any code outside the function definition
- The function should be self-contained and production-ready

Example format:
```python
def function_name(param: type) -> return_type:
    \"\"\"
    Brief description of what the function does.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception might be raised
    \"\"\"
    # Implementation here
    pass
```
"""
    
    try:
        response = llm([HumanMessage(content=prompt)])
        code = response.content
        
        if not isinstance(code, str):
            code = str(code)
        
        # Clean up the code
        code = code.strip()
        
        # Remove markdown code blocks if present
        if code.startswith('```python'):
            code = code[9:].strip()
        elif code.startswith('```'):
            code = code[3:].strip()
        
        if code.endswith('```'):
            code = code[:-3].strip()
        
        return textwrap.dedent(code).strip()
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate tool code: {e}")

def generate_tool_code_with_context(request: str, existing_tools: dict, suggested_name: Optional[str] = None) -> str:
    """
    Generate tool code with awareness of existing tools to avoid duplication.
    
    Args:
        request: Description of what the tool should do
        existing_tools: Dictionary of existing tool names and descriptions
        suggested_name: Optional suggested function name
    
    Returns:
        Generated Python function code as a string
    """
    existing_tools_info = ""
    if existing_tools:
        existing_tools_info = "\n\nExisting tools (avoid duplicating functionality):\n"
        for name, description in existing_tools.items():
            existing_tools_info += f"- {name}: {description}\n"
    
    name_hint = f"\n- Use the function name: {suggested_name}" if suggested_name else ""
    
    prompt = f"""
Write a Python function that fulfills this request: "{request}"

Requirements:
- Output exactly one top-level function definition (def ...)
- Use only standard library modules (import statements allowed)
- Include comprehensive type hints and a detailed docstring
- Make the function name descriptive and lowercase with underscores{name_hint}
- Handle edge cases and errors gracefully
- Include parameter validation where appropriate
- Return meaningful results or raise appropriate exceptions
- Do not include any code outside the function definition
- The function should be self-contained and production-ready
- Make sure this tool provides unique functionality not covered by existing tools{existing_tools_info}

Focus on creating a tool that complements existing capabilities rather than duplicating them.
"""
    
    try:
        response = llm([HumanMessage(content=prompt)])
        code = response.content
        
        if not isinstance(code, str):
            code = str(code)
        
        # Clean up the code
        code = code.strip()
        
        # Remove markdown code blocks if present
        if code.startswith('```python'):
            code = code[9:].strip()
        elif code.startswith('```'):
            code = code[3:].strip()
        
        if code.endswith('```'):
            code = code[:-3].strip()
        
        return textwrap.dedent(code).strip()
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate tool code with context: {e}")

def validate_generated_code(code: str) -> tuple[bool, str]:
    """
    Validate that the generated code is syntactically correct and safe.
    
    Args:
        code: The generated Python code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Try to compile the code
        compile(code, '<generated>', 'exec')
        
        # Basic safety checks
        dangerous_patterns = [
            'exec(',
            'eval(',
            '__import__',
            'os.system',
            'subprocess',
            'open(',  # This might be too restrictive, could be adjusted
            'file(',
            'input(',  # Interactive input not suitable for tools
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return False, f"Code contains potentially unsafe pattern: {pattern}"
        
        return True, "Code validation passed"
        
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"
