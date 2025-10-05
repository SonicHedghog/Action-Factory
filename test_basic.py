#!/usr/bin/env python3
"""
Basic test script to verify Action Factory functionality without API keys.
"""
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        from config import config, print_config_status
        print("✅ config module imported")
        
        from registry import tool_registry, register_tool
        print("✅ registry module imported")
        
        from default_tools import init_default_tools
        print("✅ default_tools module imported")
        
        # Test basic tool registration
        def test_tool(x: str) -> str:
            """A simple test tool for testing purposes."""
            return f"Test result: {x}"
        
        register_tool("test_tool", test_tool, "A simple test tool")
        print("✅ Tool registration works")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration system."""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import config
        
        # Test basic config access
        print(f"   Default model: {config.DEFAULT_MODEL}")
        print(f"   Auto tool creation: {config.ENABLE_AUTO_TOOL_CREATION}")
        print(f"   Code validation: {config.ENABLE_CODE_VALIDATION}")
        
        # Test validation (without requiring API keys)
        validation = config.validate()
        print(f"   Config valid: {validation['valid']}")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_default_tools():
    """Test default tools initialization."""
    print("\n🧪 Testing default tools...")
    
    try:
        from default_tools import init_default_tools
        from registry import tool_registry
        
        # Clear registry first
        tool_registry.clear()
        print(f"   Registry cleared: {len(tool_registry)} tools")
        
        # Initialize default tools
        init_default_tools()
        print(f"   Default tools loaded: {len(tool_registry)} tools")
        
        # Test a simple tool
        if "calculate_math" in tool_registry:
            math_tool = tool_registry["calculate_math"]
            result = math_tool.func("2 + 2")
            print(f"   Math tool test: {result}")
        
        return True
    except Exception as e:
        print(f"❌ Default tools error: {e}")
        return False

def test_code_validation():
    """Test code validation without LLM."""
    print("\n🧪 Testing code validation...")
    
    try:
        from codegen import validate_generated_code
        
        # Test valid code
        valid_code = """
def hello_world(name: str) -> str:
    return f"Hello, {name}!"
"""
        
        is_valid, message = validate_generated_code(valid_code)
        print(f"   Valid code test: {is_valid} - {message}")
        
        # Test invalid code
        invalid_code = """
def dangerous_code():
    import os
    os.system("rm -rf /")
"""
        
        is_valid, message = validate_generated_code(invalid_code)
        print(f"   Invalid code test: {is_valid} - {message}")
        
        return True
    except Exception as e:
        print(f"❌ Code validation error: {e}")
        return False

def main():
    """Run basic tests."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  ACTION FACTORY TESTS                       ║
║                   Basic Functionality                       ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    tests = [
        test_imports,
        test_config,
        test_default_tools,
        test_code_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        print("\nTo run the full system:")
        print("1. Set up your GEMINI_API_KEY in .env file")
        print("2. Run: python src/main.py")
        print("3. Or try the demo: python demo.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)