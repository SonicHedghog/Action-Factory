#!/usr/bin/env python3
"""
Example script demonstrating the Action Factory AI system capabilities.
"""
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from planner import intelligent_plan_and_execute
from registry import tool_registry, load_registry
from default_tools import init_default_tools
from config import print_config_status

def demo_basic_functionality():
    """Demonstrate basic functionality of the system."""
    print("🎯 Demo: Basic Functionality")
    print("="*50)
    
    # Initialize the system
    load_registry()
    init_default_tools()
    
    print(f"📊 Initial tools available: {len(tool_registry)}")
    for name in tool_registry.keys():
        print(f"   - {name}")
    
    print("\n🧪 Testing example requests:")
    
    # Test requests that should use existing tools
    test_requests = [
        "What time is it right now?",
        "Calculate 25 * 4 + 10",
        "Generate a random number between 1 and 50",
        "Analyze this text: 'Hello world! This is a test sentence.'",
    ]
    
    for request in test_requests:
        print(f"\n🔍 Request: {request}")
        try:
            results = intelligent_plan_and_execute(request)
            print(f"✅ Results: {results}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Final tools available: {len(tool_registry)}")

def demo_tool_creation():
    """Demonstrate automatic tool creation."""
    print("\n🎯 Demo: Automatic Tool Creation")
    print("="*50)
    
    # Test requests that should trigger tool creation
    creation_requests = [
        "Convert 100 fahrenheit to celsius",
        "Calculate the area of a circle with radius 5",
        "Create a simple hash of the text 'hello world'",
    ]
    
    for request in creation_requests:
        print(f"\n🔧 Request (should create new tool): {request}")
        tools_before = len(tool_registry)
        try:
            results = intelligent_plan_and_execute(request)
            tools_after = len(tool_registry)
            
            if tools_after > tools_before:
                print(f"✅ New tool created! Tools: {tools_before} → {tools_after}")
                print(f"   Results: {results}")
            else:
                print(f"ℹ️  No new tool needed. Results: {results}")
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_api_requests():
    """Demonstrate complex requests that require planning."""
    print("\n🎯 Demo: Complex Planning")
    print("="*50)
    
    complex_requests = [
        "I need to plan a birthday party. Help me calculate costs and create a checklist.",
        "Create a tool to validate email addresses and then check if 'test@example.com' is valid",
        "Help me convert some measurements: 5 feet to meters, 10 pounds to kilograms",
    ]
    
    for request in complex_requests:
        print(f"\n🧠 Complex request: {request}")
        try:
            results = intelligent_plan_and_execute(request)
            print(f"✅ Planning complete: {results}")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Run the demonstration."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                   ACTION FACTORY DEMO                       ║
║              AI-Powered Tool Creation Demo                  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Check configuration
    if not print_config_status():
        print("\n❌ Please set up your GEMINI_API_KEY before running the demo.")
        return
    
    try:
        demo_basic_functionality()
        demo_tool_creation()
        demo_api_requests()
        
        print("\n🎉 Demo completed successfully!")
        print(f"📊 Total tools created: {len(tool_registry)}")
        print("\nAvailable tools:")
        for name, tool in tool_registry.items():
            desc = getattr(tool, 'description', 'No description')
            print(f"   - {name}: {desc}")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()