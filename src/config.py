"""
Configuration settings for the Action Factory AI system
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the Action Factory system."""
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')
    
    # Model Configuration
    DEFAULT_MODEL = os.getenv('GOOGLE_MODEL', 'gemini-2.5-pro')
    PLANNER_MODEL = os.getenv('PLANNER_MODEL', 'gemini-2.5-pro')
    CODEGEN_MODEL = os.getenv('CODEGEN_MODEL', 'gemini-2.5-pro')
    
    # LLM Parameters
    PLANNER_TEMPERATURE = float(os.getenv('PLANNER_TEMPERATURE', '0.3'))
    CODEGEN_TEMPERATURE = float(os.getenv('CODEGEN_TEMPERATURE', '0.0'))
    AGENT_TEMPERATURE = float(os.getenv('AGENT_TEMPERATURE', '0.7'))
    
    # Planning Configuration
    MAX_PLANNING_ITERATIONS = int(os.getenv('MAX_PLANNING_ITERATIONS', '3'))
    ENABLE_AUTO_TOOL_CREATION = os.getenv('ENABLE_AUTO_TOOL_CREATION', 'true').lower() == 'true'
    REQUIRE_TOOL_VALIDATION = os.getenv('REQUIRE_TOOL_VALIDATION', 'true').lower() == 'true'
    
    # Tool Safety Configuration
    ENABLE_CODE_VALIDATION = os.getenv('ENABLE_CODE_VALIDATION', 'true').lower() == 'true'
    DANGEROUS_PATTERNS = [
        'exec(',
        'eval(',
        '__import__',
        'os.system',
        'subprocess.call',
        'subprocess.run',
        'subprocess.Popen',
        'input(',
        'raw_input(',
    ]
    
    # Registry Configuration
    REGISTRY_FILE = os.getenv('REGISTRY_FILE', 'tool_registry.json')
    AUTO_SAVE_REGISTRY = os.getenv('AUTO_SAVE_REGISTRY', 'true').lower() == 'true'
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    API_TITLE = "Action Factory AI API"
    API_VERSION = "2.0"
    
    # Networking Configuration
    ENABLE_PEER_BROADCAST = os.getenv('ENABLE_PEER_BROADCAST', 'true').lower() == 'true'
    BROADCAST_HOST = os.getenv('BROADCAST_HOST', 'localhost')
    BROADCAST_PORT = int(os.getenv('BROADCAST_PORT', '9999'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    ENABLE_VERBOSE_LOGGING = os.getenv('ENABLE_VERBOSE_LOGGING', 'false').lower() == 'true'
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status."""
        issues = []
        warnings = []
        
        # Check required API keys
        if not cls.GEMINI_API_KEY:
            issues.append("GEMINI_API_KEY is required but not set")
        
        # Check optional but recommended keys
        if not cls.GOOGLE_API_KEY or not cls.GOOGLE_CSE_ID:
            warnings.append("Google Search API not configured - search functionality will be limited")
        
        # Validate numeric values
        if cls.PLANNER_TEMPERATURE < 0 or cls.PLANNER_TEMPERATURE > 1:
            issues.append("PLANNER_TEMPERATURE must be between 0 and 1")
        
        if cls.CODEGEN_TEMPERATURE < 0 or cls.CODEGEN_TEMPERATURE > 1:
            issues.append("CODEGEN_TEMPERATURE must be between 0 and 1")
        
        if cls.AGENT_TEMPERATURE < 0 or cls.AGENT_TEMPERATURE > 1:
            issues.append("AGENT_TEMPERATURE must be between 0 and 1")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "config": {
                "model": cls.DEFAULT_MODEL,
                "auto_tool_creation": cls.ENABLE_AUTO_TOOL_CREATION,
                "tool_validation": cls.REQUIRE_TOOL_VALIDATION,
                "code_validation": cls.ENABLE_CODE_VALIDATION,
                "api_enabled": True,
                "peer_broadcast": cls.ENABLE_PEER_BROADCAST
            }
        }
    
    @classmethod
    def get_llm_config(cls, llm_type: str = "default") -> Dict[str, Any]:
        """Get LLM configuration for different use cases."""
        base_config = {
            "google_api_key": cls.GEMINI_API_KEY,
            "model": cls.DEFAULT_MODEL
        }
        
        if llm_type == "planner":
            base_config.update({
                "model": cls.PLANNER_MODEL,
                "temperature": cls.PLANNER_TEMPERATURE
            })
        elif llm_type == "codegen":
            base_config.update({
                "model": cls.CODEGEN_MODEL,
                "temperature": cls.CODEGEN_TEMPERATURE
            })
        elif llm_type == "agent":
            base_config.update({
                "temperature": cls.AGENT_TEMPERATURE
            })
        
        return base_config

# Global configuration instance
config = Config()

def print_config_status():
    """Print current configuration status."""
    validation = config.validate()
    
    print("🔧 Action Factory Configuration Status")
    print("=" * 50)
    
    if validation["valid"]:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has issues:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
    
    if validation["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in validation["warnings"]:
            print(f"   - {warning}")
    
    print(f"\n📊 Current Settings:")
    for key, value in validation["config"].items():
        print(f"   - {key}: {value}")
    
    print(f"\n🤖 Model Configuration:")
    print(f"   - Default Model: {config.DEFAULT_MODEL}")
    print(f"   - Planner Temperature: {config.PLANNER_TEMPERATURE}")
    print(f"   - Codegen Temperature: {config.CODEGEN_TEMPERATURE}")
    print(f"   - Agent Temperature: {config.AGENT_TEMPERATURE}")
    
    return validation["valid"]