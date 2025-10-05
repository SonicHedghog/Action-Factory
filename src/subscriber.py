import json
import threading
import time
import uuid
from database import db_manager
from registry import register_tool
from typing import Dict

# Generate a unique subscriber ID for this instance
SUBSCRIBER_ID = f"subscriber_{uuid.uuid4().hex[:8]}"

def _handle_event(event: Dict) -> None:
    name = event["name"]
    code = event["code"]
    description = event.get("description", "")
    # exec into a fresh namespace then register
    ns = {}
    try:
        exec(code, ns)
        func = ns.get(name)
        if func is None:
            print(f"Received tool {name} but could not locate function after exec.")
            return
        register_tool(name, func, description)
        print(f"Imported remote tool: {name}")
    except Exception as e:
        print(f"Error processing tool {name}: {e}")

def listen_for_tools() -> None:
    print(f"Subscriber {SUBSCRIBER_ID}: listening for tool updates...")
    while True:
        try:
            # Poll for new tool updates
            updates = db_manager.get_new_tool_updates(SUBSCRIBER_ID)
            for update in updates:
                event = {
                    "name": update["name"],
                    "description": update["description"] or "",
                    "code": update["code"]
                }
                _handle_event(event)
            
            # Sleep between polls to avoid excessive database queries
            time.sleep(2)
        except Exception as e:
            print(f"Error in tool listener: {e}")
            time.sleep(5)  # Wait longer on error

def start_background_listener() -> threading.Thread:
    # Initialize database schema if needed
    try:
        db_manager.init_database()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")
    
    t = threading.Thread(target=listen_for_tools, daemon=True)
    t.start()
    return t