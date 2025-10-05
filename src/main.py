"""
Action Factory - AI-Powered Tool Creation and Execution System
Main entry point for the application.
"""
import sys
from config import config, print_config_status
from registry import load_registry
from subscriber import start_background_listener
from agent import run_agent_loop
from default_tools import init_default_tools

def print_banner():
    """Print the application banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                        ACTION FACTORY                        ║
║                  AI-Powered Tool Creation                    ║
║                        Version 2.0                          ║
╚══════════════════════════════════════════════════════════════╝
""")

def main():
    """Main application entry point."""
    print_banner()
    
    # Validate configuration
    print("🔧 Checking configuration...")
    if not print_config_status():
        print("\n❌ Configuration validation failed. Please check your environment variables.")
        print("   Required: GEMINI_API_KEY")
        print("   Optional: GOOGLE_API_KEY, GOOGLE_CSE_ID")
        sys.exit(1)
    
    print("\n🚀 Starting Action Factory...")
    
    try:
        # Load existing tool registry
        print("📂 Loading tool registry...")
        load_registry()
        
        # Initialize default tools
        print("🛠️  Initializing default tools...")
        init_default_tools()
        
        # Start background listener for peer communication
        if config.ENABLE_PEER_BROADCAST:
            print("📡 Starting peer communication listener...")
            start_background_listener()
        else:
            print("📡 Peer communication disabled")
        
        # Start the main agent loop
        print("🤖 Starting AI agent...")
        print("="*60)
        run_agent_loop()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutdown requested by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    finally:
        print("🛑 Action Factory shutdown complete.")

if __name__ == "__main__":
    main()