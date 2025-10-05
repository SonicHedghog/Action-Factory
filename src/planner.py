import re
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from registry import tool_registry, register_tool
from codegen import generate_tool_code_with_context, validate_generated_code
from testgen import generate_property_test
from sandbox import run_property_test
from broadcaster import broadcast_tool

# Load environment variables
load_dotenv()

# Get the API key from environment variables
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in your .env file.")

# Initialize the LLM for planning
planner_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro", 
    temperature=0.3, 
    google_api_key=gemini_api_key
)

def extract_function_name(func_code: str) -> str:
    """Extract function name from generated code."""
    m = re.search(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", func_code, re.M)
    if not m:
        raise ValueError("Could not find function name in code")
    return m.group(1)

def get_available_tools_description() -> str:
    """Get a formatted description of all available tools."""
    if not tool_registry:
        return "No tools are currently available in the registry."
    
    tools_desc = "Available tools:\n"
    for name, tool in tool_registry.items():
        description = getattr(tool, 'description', 'No description available')
        tools_desc += f"- {name}: {description}\n"
    
    return tools_desc

def analyze_user_request(user_instruction: str) -> Dict[str, Any]:
    """
    Use LLM to analyze the user request and determine what needs to be done.
    Returns a structured analysis including whether existing tools can handle it.
    """
    tools_info = get_available_tools_description()
    
    analysis_prompt = f"""
Analyze the following user request and the available tools, then provide a structured response.

User Request: "{user_instruction}"

{tools_info}

Please analyze this request and respond with a JSON object containing:
1. "task_type": One of ["use_existing_tools", "need_new_tool", "complex_workflow", "clarification_needed"]
2. "confidence": A number from 0.0 to 1.0 indicating confidence in the analysis
3. "reasoning": Brief explanation of the analysis
4. "existing_tools_sufficient": boolean indicating if current tools can handle this
5. "required_capabilities": list of specific capabilities needed
6. "suggested_approach": recommended approach to handle this request

If existing tools can handle it:
7. "recommended_tools": list of tool names that should be used
8. "execution_plan": step-by-step plan using existing tools

If new tools are needed:
7. "missing_tool_description": description of what new tool should do
8. "tool_name_suggestion": suggested name for the new tool

Respond only with valid JSON.
"""
    
    try:
        response = planner_llm([HumanMessage(content=analysis_prompt)])
        analysis_text = response.content.strip()
        
        # Try to extract JSON from the response
        if analysis_text.startswith('```json'):
            analysis_text = analysis_text[7:-3].strip()
        elif analysis_text.startswith('```'):
            analysis_text = analysis_text[3:-3].strip()
        
        analysis = json.loads(analysis_text)
        return analysis
    except Exception as e:
        print(f"Error analyzing request: {e}")
        # Fallback analysis
        return {
            "task_type": "clarification_needed",
            "confidence": 0.1,
            "reasoning": f"Failed to analyze request due to error: {str(e)}",
            "existing_tools_sufficient": False,
            "required_capabilities": ["unknown"],
            "suggested_approach": "manual_analysis"
        }

def create_execution_plan(user_instruction: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Create a detailed execution plan based on the analysis.
    """
    task_type = analysis.get("task_type")
    
    if task_type == "use_existing_tools":
        # Create plan using existing tools
        recommended_tools = analysis.get("recommended_tools", [])
        execution_plan = analysis.get("execution_plan", [])
        
        if not execution_plan and recommended_tools:
            # Generate a simple plan if none provided
            plan = []
            for tool_name in recommended_tools:
                if tool_name in tool_registry:
                    plan.append({
                        "action": "use_tool",
                        "tool": tool_name,
                        "args": {"instruction": user_instruction},
                        "reasoning": f"Using {tool_name} to handle part of the request"
                    })
            return plan
        else:
            # Convert the execution plan to our format
            plan = []
            for step in execution_plan:
                if isinstance(step, str):
                    # Simple string step - try to match to a tool
                    for tool_name in tool_registry.keys():
                        if tool_name.lower() in step.lower():
                            plan.append({
                                "action": "use_tool",
                                "tool": tool_name,
                                "args": {"instruction": user_instruction},
                                "reasoning": step
                            })
                            break
                elif isinstance(step, dict):
                    plan.append(step)
            return plan
    
    elif task_type == "need_new_tool":
        return [{
            "action": "create_new_tool",
            "tool_description": analysis.get("missing_tool_description", user_instruction),
            "tool_name": analysis.get("tool_name_suggestion", ""),
            "reasoning": analysis.get("reasoning", "New tool needed")
        }]
    
    elif task_type == "complex_workflow":
        # For complex workflows, we might need multiple tools or steps
        return [{
            "action": "complex_workflow",
            "description": user_instruction,
            "reasoning": analysis.get("reasoning", "Complex workflow detected"),
            "suggested_approach": analysis.get("suggested_approach", "break_down_further")
        }]
    
    else:  # clarification_needed
        return [{
            "action": "request_clarification",
            "message": f"I need more information to understand your request: {user_instruction}",
            "reasoning": analysis.get("reasoning", "Request unclear")
        }]

def execute_plan_step(step: Dict[str, Any]) -> Optional[Any]:
    """
    Execute a single step from the execution plan.
    """
    action = step.get("action")
    
    if action == "use_tool":
        tool_name = step.get("tool")
        args = step.get("args", {})
        
        if tool_name in tool_registry:
            try:
                tool = tool_registry[tool_name]
                # For now, pass the instruction directly
                instruction = args.get("instruction", "")
                result = tool.func(instruction) if hasattr(tool, 'func') else tool.run(instruction)
                print(f"✓ Executed {tool_name}: {step.get('reasoning', '')}")
                return result
            except Exception as e:
                print(f"✗ Error executing {tool_name}: {e}")
                return f"Error: {e}"
        else:
            print(f"✗ Tool {tool_name} not found in registry")
            return None
    
    elif action == "create_new_tool":
        return create_and_register_new_tool(
            step.get("tool_description", ""),
            step.get("tool_name", "")
        )
    
    elif action == "request_clarification":
        print(f"🤔 {step.get('message', 'Need clarification')}")
        return step.get("message")
    
    elif action == "complex_workflow":
        print(f"🔄 Complex workflow detected: {step.get('description', '')}")
        print(f"   Suggested approach: {step.get('suggested_approach', '')}")
        return step.get("description")
    
    else:
        print(f"❓ Unknown action: {action}")
        return None

def create_and_register_new_tool(tool_description: str, suggested_name: str = "") -> bool:
    """
    Create, test, and register a new tool based on the description.
    """
    print(f"🛠️  Creating new tool: {tool_description}")
    
    try:
        # Get existing tools info for context
        existing_tools = {name: getattr(tool, 'description', 'No description') 
                         for name, tool in tool_registry.items()}
        
        # Generate the tool code with context awareness
        func_code = generate_tool_code_with_context(
            tool_description, 
            existing_tools, 
            suggested_name if suggested_name else None
        )
        
        # Validate the generated code
        is_valid, validation_message = validate_generated_code(func_code)
        if not is_valid:
            print(f"   ✗ Generated code validation failed: {validation_message}")
            return False
        
        func_name = extract_function_name(func_code)
        
        if suggested_name and suggested_name != func_name:
            print(f"   Generated name: {func_name} (suggested: {suggested_name})")
        else:
            print(f"   Generated function: {func_name}")
        
        # Generate and run tests
        test_code = generate_property_test(func_name, func_code)
        print("   Running property tests...")
        
        passed, output = run_property_test(func_code, test_code)
        print(f"   Test output: {output}")
        
        if not passed:
            print("   ✗ Property tests failed; aborting tool registration.")
            return False
        
        # Execute and register the tool
        ns = {}
        exec(func_code, ns)
        func = ns.get(func_name)
        
        if func is None:
            print("   ✗ Failed to import generated function after exec.")
            return False
        
        # Register the tool
        register_tool(func_name, func, func.__doc__ or tool_description)
        print(f"   ✓ Tool {func_name} registered successfully")
        
        # Broadcast to peers
        broadcast_tool(func_name, func.__doc__ or tool_description, func_code)
        print(f"   📡 Tool broadcasted to peer nodes")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error creating tool: {e}")
        return False

def intelligent_plan_and_execute(user_instruction: str) -> List[Any]:
    """
    Main intelligent planning function that analyzes the request,
    creates a plan, and executes it step by step.
    """
    print(f"🧠 Analyzing request: {user_instruction}")
    
    # Analyze the user request
    analysis = analyze_user_request(user_instruction)
    
    print(f"   Task type: {analysis.get('task_type')}")
    print(f"   Confidence: {analysis.get('confidence', 0):.2f}")
    print(f"   Reasoning: {analysis.get('reasoning', 'No reasoning provided')}")
    
    # Create execution plan
    execution_plan = create_execution_plan(user_instruction, analysis)
    
    if not execution_plan:
        print("   ❌ No execution plan could be created")
        return []
    
    print(f"   📋 Created plan with {len(execution_plan)} steps")
    
    # Execute the plan
    results = []
    for i, step in enumerate(execution_plan, 1):
        print(f"\n🔄 Step {i}/{len(execution_plan)}: {step.get('action', 'unknown')}")
        result = execute_plan_step(step)
        results.append(result)
        
        # If we created a new tool, we might want to re-analyze and continue
        if step.get("action") == "create_new_tool" and result:
            print("   🔄 Re-analyzing with new tool available...")
            # Re-run analysis now that we have a new tool
            new_analysis = analyze_user_request(user_instruction)
            if new_analysis.get("existing_tools_sufficient"):
                additional_plan = create_execution_plan(user_instruction, new_analysis)
                for additional_step in additional_plan:
                    if additional_step.get("action") == "use_tool":
                        print(f"🔄 Additional step: Using newly created tool")
                        additional_result = execute_plan_step(additional_step)
                        results.append(additional_result)
    
    return results

# Legacy compatibility functions
def plan_workflow_with_registry(user_instruction: str):
    """
    Legacy function for backward compatibility.
    Now delegates to the intelligent planner.
    """
    results = intelligent_plan_and_execute(user_instruction)
    
    # Convert results to legacy format
    if results:
        # Find any tool usage in the results
        for result in results:
            if result is not None:
                # Try to find which tool was used
                for name in tool_registry:
                    if name.lower() in user_instruction.lower():
                        return [{"tool": name, "args": {"instruction": user_instruction}}]
        
        # If no specific tool match, return a generic result
        return [{"result": results[0] if results else "No result"}]
    
    return []

def plan_or_generate(user_instruction: str):
    """
    Legacy function for backward compatibility.
    Now delegates to the intelligent planner.
    """
    return intelligent_plan_and_execute(user_instruction)