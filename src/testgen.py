import textwrap
import os
from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0, google_api_key=gemini_api_key)


def generate_property_test(func_name: str, func_code: str) -> str:
    prompt = f"""
Write a pytest test using Hypothesis for the following Python function:

{func_code}

Requirements:
- Import hypothesis and hypothesis.strategies as st
- Define at least one property-based test using @given(...)
- Name the test function: test_{func_name}_properties
- Only output the test function definition (no extra text)
"""
    test_code = llm([HumanMessage(content=prompt)]).content
    if not isinstance(test_code, str):
        test_code = str(test_code)
    return textwrap.dedent(test_code).strip()
