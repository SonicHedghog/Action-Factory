from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from registry import register_tool, tool_registry
from planner import intelligent_plan_and_execute, analyze_user_request, get_available_tools_description
from codegen import generate_tool_code_with_context, validate_generated_code

app = FastAPI(title="Action Factory API", description="API for AI-powered tool creation and execution")

class ToolSpec(BaseModel):
    name: str
    description: str
    code: str

class PlanRequest(BaseModel):
    instruction: str
    context: Optional[str] = None

class PlanResponse(BaseModel):
    analysis: Dict[str, Any]
    execution_plan: List[Dict[str, Any]]
    success: bool
    message: str

class ExecuteRequest(BaseModel):
    instruction: str
    auto_create_tools: bool = True

class ExecuteResponse(BaseModel):
    results: List[Any]
    success: bool
    message: str
    tools_created: List[str]

class ToolGenerationRequest(BaseModel):
    description: str
    suggested_name: Optional[str] = None

class ToolGenerationResponse(BaseModel):
    success: bool
    tool_name: Optional[str] = None
    code: Optional[str] = None
    message: str

@app.get("/")
def root():
    """API health check and basic info."""
    return {
        "message": "Action Factory API",
        "version": "2.0",
        "features": [
            "Intelligent planning",
            "Automatic tool creation",
            "Tool execution",
            "Tool management"
        ],
        "tools_available": len(tool_registry)
    }

@app.get("/tools")
def list_tools():
    """List all available tools."""
    tools = {}
    for name, tool in tool_registry.items():
        tools[name] = {
            "name": name,
            "description": getattr(tool, 'description', 'No description available')
        }
    return {
        "tools": tools,
        "count": len(tools)
    }

@app.post("/tools/add")
def add_tool(spec: ToolSpec):
    """Add a new tool manually."""
    try:
        # Validate the code first
        is_valid, validation_message = validate_generated_code(spec.code)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Code validation failed: {validation_message}")
        
        # Execute the code
        namespace = {}
        exec(spec.code, namespace)
        
        # Get the function
        func = namespace.get(spec.name)
        if func is None:
            raise HTTPException(status_code=400, detail=f"Function {spec.name} not found in provided code")
        
        # Register the tool
        register_tool(spec.name, func, spec.description)
        
        return {
            "status": "success",
            "message": f"Tool {spec.name} added successfully",
            "tool_name": spec.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding tool: {str(e)}")

@app.post("/tools/generate", response_model=ToolGenerationResponse)
def generate_tool(request: ToolGenerationRequest):
    """Generate a new tool based on description."""
    try:
        # Get existing tools for context
        existing_tools = {name: getattr(tool, 'description', 'No description') 
                         for name, tool in tool_registry.items()}
        
        # Generate the tool code
        code = generate_tool_code_with_context(
            request.description,
            existing_tools,
            request.suggested_name
        )
        
        # Validate the code
        is_valid, validation_message = validate_generated_code(code)
        if not is_valid:
            return ToolGenerationResponse(
                success=False,
                message=f"Generated code validation failed: {validation_message}"
            )
        
        # Extract function name
        import re
        match = re.search(r"^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", code, re.M)
        if not match:
            return ToolGenerationResponse(
                success=False,
                message="Could not extract function name from generated code"
            )
        
        function_name = match.group(1)
        
        return ToolGenerationResponse(
            success=True,
            tool_name=function_name,
            code=code,
            message=f"Tool {function_name} generated successfully"
        )
        
    except Exception as e:
        return ToolGenerationResponse(
            success=False,
            message=f"Error generating tool: {str(e)}"
        )

@app.post("/plan", response_model=PlanResponse)
def create_plan(request: PlanRequest):
    """Analyze a request and create an execution plan."""
    try:
        # Analyze the request
        analysis = analyze_user_request(request.instruction)
        
        # Create execution plan (this is done internally by intelligent_plan_and_execute)
        # For now, we'll return the analysis and a basic plan structure
        
        return PlanResponse(
            analysis=analysis,
            execution_plan=[],  # This would be populated by the planning logic
            success=True,
            message="Plan created successfully"
        )
        
    except Exception as e:
        return PlanResponse(
            analysis={},
            execution_plan=[],
            success=False,
            message=f"Error creating plan: {str(e)}"
        )

@app.post("/execute", response_model=ExecuteResponse)
def execute_instruction(request: ExecuteRequest):
    """Execute an instruction using intelligent planning."""
    try:
        tools_before = set(tool_registry.keys())
        
        # Execute using intelligent planning
        results = intelligent_plan_and_execute(request.instruction)
        
        tools_after = set(tool_registry.keys())
        tools_created = list(tools_after - tools_before)
        
        return ExecuteResponse(
            results=results,
            success=True,
            message="Instruction executed successfully",
            tools_created=tools_created
        )
        
    except Exception as e:
        return ExecuteResponse(
            results=[],
            success=False,
            message=f"Error executing instruction: {str(e)}",
            tools_created=[]
        )

@app.get("/status")
def get_status():
    """Get system status and available tools."""
    return {
        "tools_available": len(tool_registry),
        "tools": get_available_tools_description(),
        "capabilities": [
            "Intelligent request analysis",
            "Automatic tool creation",
            "Tool validation and testing",
            "Execution planning",
            "Peer-to-peer tool sharing"
        ]
    }

@app.delete("/tools/{tool_name}")
def remove_tool(tool_name: str):
    """Remove a tool from the registry."""
    if tool_name not in tool_registry:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
    
    del tool_registry[tool_name]
    return {
        "status": "success",
        "message": f"Tool {tool_name} removed successfully"
    }

@app.delete("/tools")
def reset_tools():
    """Reset all tools."""
    from registry import reset_registry
    reset_registry()
    return {
        "status": "success",
        "message": "All tools cleared successfully"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)