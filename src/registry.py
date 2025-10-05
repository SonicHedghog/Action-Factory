import json, os
from langchain_core.tools import tool

REGISTRY_FILE = "tool_registry.json"
tool_registry = {}

def save_registry():
    try:
        with open(REGISTRY_FILE, "w") as f:
            json.dump({name: {"description": t.description} for name, t in tool_registry.items()}, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save registry: {e}")

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r") as f:
                data = json.load(f)
            for name, meta in data.items():
                print(f"Found saved tool metadata: {name} — {meta['description']}")
                # Note: Tool implementations will be loaded when they are re-registered
                # or when received via the subscriber system
        except json.JSONDecodeError as e:
            print(f"Warning: Could not load registry file {REGISTRY_FILE}: {e}")
            print("Starting with empty registry...")
        except Exception as e:
            print(f"Warning: Error loading registry: {e}")
            print("Starting with empty registry...")

def register_tool(name, func, description):
    wrapped = tool(func)
    tool_registry[name] = wrapped
    save_registry()

def reset_registry():
    """Reset the tool registry and clear the registry file"""
    global tool_registry
    tool_registry.clear()
    try:
        if os.path.exists(REGISTRY_FILE):
            os.remove(REGISTRY_FILE)
        print("Registry reset successfully")
    except Exception as e:
        print(f"Warning: Could not reset registry file: {e}")