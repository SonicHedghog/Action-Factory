from database import db_manager

def broadcast_tool(name, description, code):
    """Broadcast a tool update to the database"""
    try:
        db_manager.publish_tool_update(name, description, code)
        print(f"Broadcasted tool: {name}")
    except Exception as e:
        print(f"Error broadcasting tool {name}: {e}")