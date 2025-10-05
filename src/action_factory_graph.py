"""
Action Factory - LangGraph Implementation
A problem-solving workflow that creates and uses tools dynamically
"""

from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionFactoryState(TypedDict):
    """State for the Action Factory workflow"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_prompt: str
    problem_steps: List[Dict[str, Any]]
    current_step_index: int
    available_tools: Dict[str, BaseTool]
    step_results: List[Dict[str, Any]]
    final_answer: str
    workflow_complete: bool


class ProblemStep:
    """Represents a single step in the problem-solving process"""
    def __init__(self, description: str, required_tools: List[str] = None, dependencies: List[int] = None):
        self.description = description
        self.required_tools = required_tools or []
        self.dependencies = dependencies or []
        self.completed = False
        self.result = None
        self.tools_created = []


class ActionFactoryGraph:
    """Main Action Factory workflow implementation using LangGraph"""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(ActionFactoryState)
        
        # Add nodes
        workflow.add_node("create_problem_steps", self.create_problem_steps)
        workflow.add_node("check_tool_exists", self.check_tool_exists)
        workflow.add_node("make_tool", self.make_tool)
        workflow.add_node("test_tool", self.test_tool)
        workflow.add_node("solve_step", self.solve_step)
        workflow.add_node("finalize_answer", self.finalize_answer)
        workflow.add_node("give_user_answer", self.give_user_answer)
        
        # Add edges
        workflow.add_edge(START, "create_problem_steps")
        workflow.add_edge("create_problem_steps", "check_tool_exists")
        
        # Conditional edges
        workflow.add_conditional_edges(
            "check_tool_exists",
            self.tool_exists_condition,
            {
                "make_tool": "make_tool",
                "solve_step": "solve_step"
            }
        )
        
        workflow.add_edge("make_tool", "test_tool")
        
        workflow.add_conditional_edges(
            "test_tool",
            self.tool_works_condition,
            {
                "solve_step": "solve_step",
                "make_tool": "make_tool"  # Retry if tool doesn't work
            }
        )
        
        workflow.add_conditional_edges(
            "solve_step",
            self.next_step_condition,
            {
                "check_tool_exists": "check_tool_exists",
                "finalize_answer": "finalize_answer"
            }
        )
        
        workflow.add_edge("finalize_answer", "give_user_answer")
        workflow.add_edge("give_user_answer", END)
        
        return workflow.compile()
    
    def create_problem_steps(self, state: ActionFactoryState) -> ActionFactoryState:
        """Break down the user prompt into problem-solving steps"""
        logger.info("Creating problem steps...")
        
        prompt = f"""
        User wants to solve: {state['user_prompt']}
        
        Break this down into clear, actionable steps. For each step, identify:
        1. What needs to be done
        2. What tools might be needed
        3. Dependencies on other steps
        
        Return a JSON list of steps with format:
        [
            {{
                "description": "step description",
                "required_tools": ["tool1", "tool2"],
                "dependencies": [0, 1]  // indices of prerequisite steps
            }}
        ]
        """
        
        if self.llm:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            try:
                steps_data = json.loads(response.content)
                problem_steps = [
                    {
                        "description": step["description"],
                        "required_tools": step.get("required_tools", []),
                        "dependencies": step.get("dependencies", []),
                        "completed": False,
                        "result": None
                    }
                    for step in steps_data
                ]
            except json.JSONDecodeError:
                # Fallback: create basic steps
                problem_steps = [
                    {
                        "description": f"Analyze and solve: {state['user_prompt']}",
                        "required_tools": ["analysis_tool"],
                        "dependencies": [],
                        "completed": False,
                        "result": None
                    }
                ]
        else:
            # Fallback when no LLM is provided
            problem_steps = [
                {
                    "description": f"Solve the problem: {state['user_prompt']}",
                    "required_tools": ["basic_solver"],
                    "dependencies": [],
                    "completed": False,
                    "result": None
                }
            ]
        
        return {
            **state,
            "problem_steps": problem_steps,
            "current_step_index": 0,
            "step_results": []
        }
    
    def check_tool_exists(self, state: ActionFactoryState) -> ActionFactoryState:
        """Check if required tools exist for the current step"""
        logger.info(f"Checking tools for step {state['current_step_index']}...")
        
        if state["current_step_index"] >= len(state["problem_steps"]):
            return state
        
        current_step = state["problem_steps"][state["current_step_index"]]
        required_tools = current_step["required_tools"]
        available_tools = state.get("available_tools", {})
        
        missing_tools = [tool for tool in required_tools if tool not in available_tools]
        
        # Add information about tool availability to messages
        if missing_tools:
            message = f"Missing tools for step {state['current_step_index']}: {missing_tools}"
        else:
            message = f"All required tools available for step {state['current_step_index']}"
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=message)]
        }
    
    def make_tool(self, state: ActionFactoryState) -> ActionFactoryState:
        """Create the required tools for the current step"""
        logger.info("Creating tools...")
        
        if state["current_step_index"] >= len(state["problem_steps"]):
            return state
        
        current_step = state["problem_steps"][state["current_step_index"]]
        required_tools = current_step["required_tools"]
        available_tools = state.get("available_tools", {})
        
        # Create missing tools (simplified implementation)
        for tool_name in required_tools:
            if tool_name not in available_tools:
                # Create a basic tool implementation
                tool = self._create_basic_tool(tool_name, current_step["description"])
                available_tools[tool_name] = tool
        
        message = f"Created tools: {[tool for tool in required_tools if tool not in state.get('available_tools', {})]}"
        
        return {
            **state,
            "available_tools": available_tools,
            "messages": state["messages"] + [AIMessage(content=message)]
        }
    
    def test_tool(self, state: ActionFactoryState) -> ActionFactoryState:
        """Test if the created tools work correctly"""
        logger.info("Testing tools...")
        
        if state["current_step_index"] >= len(state["problem_steps"]):
            return state
        
        current_step = state["problem_steps"][state["current_step_index"]]
        required_tools = current_step["required_tools"]
        available_tools = state.get("available_tools", {})
        
        # Test each required tool
        tool_test_results = {}
        for tool_name in required_tools:
            if tool_name in available_tools:
                tool = available_tools[tool_name]
                try:
                    # Basic test - just check if tool can be called
                    test_result = self._test_tool(tool, current_step["description"])
                    tool_test_results[tool_name] = test_result
                except Exception as e:
                    tool_test_results[tool_name] = False
                    logger.error(f"Tool {tool_name} failed test: {e}")
        
        all_tools_work = all(tool_test_results.values())
        message = f"Tool test results: {tool_test_results}. All working: {all_tools_work}"
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=message)]
        }
    
    def solve_step(self, state: ActionFactoryState) -> ActionFactoryState:
        """Solve the current step using available tools"""
        logger.info(f"Solving step {state['current_step_index']}...")
        
        if state["current_step_index"] >= len(state["problem_steps"]):
            return state
        
        current_step = state["problem_steps"][state["current_step_index"]]
        available_tools = state.get("available_tools", {})
        
        # Use tools to solve the step
        step_result = self._solve_with_tools(current_step, available_tools)
        
        # Mark step as completed
        updated_steps = state["problem_steps"].copy()
        updated_steps[state["current_step_index"]]["completed"] = True
        updated_steps[state["current_step_index"]]["result"] = step_result
        
        step_results = state.get("step_results", [])
        step_results.append({
            "step_index": state["current_step_index"],
            "description": current_step["description"],
            "result": step_result
        })
        
        message = f"Completed step {state['current_step_index']}: {current_step['description']}"
        
        return {
            **state,
            "problem_steps": updated_steps,
            "step_results": step_results,
            "current_step_index": state["current_step_index"] + 1,
            "messages": state["messages"] + [AIMessage(content=message)]
        }
    
    def finalize_answer(self, state: ActionFactoryState) -> ActionFactoryState:
        """Finalize the answer using user prompts and step results"""
        logger.info("Finalizing answer...")
        
        step_results = state.get("step_results", [])
        user_prompt = state["user_prompt"]
        
        # Combine all step results into a final answer
        if self.llm:
            prompt = f"""
            Original user request: {user_prompt}
            
            Step results:
            {json.dumps(step_results, indent=2)}
            
            Please provide a comprehensive final answer that addresses the user's original request,
            incorporating all the step results.
            """
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            final_answer = response.content
        else:
            # Fallback answer
            final_answer = f"Solved '{user_prompt}' through {len(step_results)} steps. Results: {[r['result'] for r in step_results]}"
        
        return {
            **state,
            "final_answer": final_answer,
            "workflow_complete": True
        }
    
    def give_user_answer(self, state: ActionFactoryState) -> ActionFactoryState:
        """Present the final answer to the user"""
        logger.info("Presenting final answer to user...")
        
        final_answer = state.get("final_answer", "No solution generated")
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=final_answer)]
        }
    
    # Condition functions for conditional edges
    
    def tool_exists_condition(self, state: ActionFactoryState) -> str:
        """Determine if tools exist for current step"""
        if state["current_step_index"] >= len(state["problem_steps"]):
            return "solve_step"
        
        current_step = state["problem_steps"][state["current_step_index"]]
        required_tools = current_step["required_tools"]
        available_tools = state.get("available_tools", {})
        
        missing_tools = [tool for tool in required_tools if tool not in available_tools]
        
        return "make_tool" if missing_tools else "solve_step"
    
    def tool_works_condition(self, state: ActionFactoryState) -> str:
        """Determine if tools work correctly"""
        # For simplicity, assume tools work after creation
        # In a real implementation, you'd check the test results
        return "solve_step"
    
    def next_step_condition(self, state: ActionFactoryState) -> str:
        """Determine if there are more steps to process"""
        return "check_tool_exists" if state["current_step_index"] < len(state["problem_steps"]) else "finalize_answer"
    
    # Helper methods
    
    def _create_basic_tool(self, tool_name: str, step_description: str) -> BaseTool:
        """Create a basic tool implementation"""
        from langchain_core.tools import tool
        
        @tool(name=tool_name)
        def basic_tool(query: str) -> str:
            """A basic tool for problem solving"""
            return f"Tool {tool_name} processed: {query} for step: {step_description}"
        
        return basic_tool
    
    def _test_tool(self, tool: BaseTool, test_input: str) -> bool:
        """Test if a tool works correctly"""
        try:
            result = tool.invoke(test_input)
            return bool(result)
        except Exception:
            return False
    
    def _solve_with_tools(self, step: Dict[str, Any], tools: Dict[str, BaseTool]) -> str:
        """Solve a step using available tools"""
        step_description = step["description"]
        required_tools = step["required_tools"]
        
        if not required_tools:
            return f"Completed: {step_description}"
        
        # Use tools to solve the step
        results = []
        for tool_name in required_tools:
            if tool_name in tools:
                tool = tools[tool_name]
                try:
                    result = tool.invoke(step_description)
                    results.append(f"{tool_name}: {result}")
                except Exception as e:
                    results.append(f"{tool_name}: Error - {str(e)}")
        
        return f"Step solved using tools. Results: {'; '.join(results)}"
    
    def run(self, user_prompt: str) -> Dict[str, Any]:
        """Run the Action Factory workflow"""
        initial_state = ActionFactoryState(
            messages=[HumanMessage(content=user_prompt)],
            user_prompt=user_prompt,
            problem_steps=[],
            current_step_index=0,
            available_tools={},
            step_results=[],
            final_answer="",
            workflow_complete=False
        )
        
        final_state = self.graph.invoke(initial_state)
        
        return {
            "final_answer": final_state.get("final_answer", ""),
            "step_results": final_state.get("step_results", []),
            "messages": final_state.get("messages", []),
            "workflow_complete": final_state.get("workflow_complete", False)
        }


# Example usage and testing
if __name__ == "__main__":
    # Create the Action Factory graph
    action_factory = ActionFactoryGraph()
    
    # Test with a sample problem
    test_prompt = "Calculate the area of a circle with radius 5 and then find how many such circles fit in a rectangle of 20x30"
    
    print("Running Action Factory workflow...")
    print(f"User prompt: {test_prompt}")
    print("-" * 50)
    
    result = action_factory.run(test_prompt)
    
    print("Workflow Results:")
    print(f"Final Answer: {result['final_answer']}")
    print(f"Workflow Complete: {result['workflow_complete']}")
    print(f"Number of steps completed: {len(result['step_results'])}")
    
    print("\nStep Details:")
    for step in result['step_results']:
        print(f"Step {step['step_index']}: {step['description']}")
        print(f"Result: {step['result']}")
        print()