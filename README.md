# Action Factory - AI-Powered Tool Creation System

An intelligent system that uses Large Language Models (LLMs) to analyze user requests, create tools dynamically, and execute complex workflows automatically.

## 🚀 Features

### Intelligent Planning
- **LLM-Powered Analysis**: Uses Google's Gemini model to understand user requests
- **Automatic Tool Detection**: Determines if existing tools can handle requests
- **Smart Tool Creation**: Generates new tools when existing ones are insufficient
- **Workflow Planning**: Creates multi-step execution plans for complex tasks

### Dynamic Tool Creation
- **Code Generation**: Automatically generates Python functions based on descriptions
- **Safety Validation**: Validates generated code for security and correctness
- **Property Testing**: Uses Hypothesis for automated testing of generated tools
- **Peer Broadcasting**: Shares new tools across multiple instances

### Rich Default Tools
- **Google Search**: Web search capabilities (with API key)
- **Math Calculator**: Safe mathematical expression evaluation
- **Text Analysis**: Word count, character analysis, and text statistics
- **Time/Date**: Current time with formatting options
- **Random Generation**: Numbers, passwords, and other random data
- **JSON Formatting**: Validate and format JSON data
- **URL Validation**: Check and analyze URL structure

## 📋 Requirements

```
langchain
langchain-openai
langchain-google-genai
langchain-community
python-dotenv
psycopg2-binary
fastapi
uvicorn
pytest
hypothesis
```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - for Google Search
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id

# Model Configuration (optional)
GOOGLE_MODEL=gemini-2.5-pro
PLANNER_TEMPERATURE=0.3
CODEGEN_TEMPERATURE=0.0
AGENT_TEMPERATURE=0.7

# System Configuration (optional)
ENABLE_AUTO_TOOL_CREATION=true
REQUIRE_TOOL_VALIDATION=true
ENABLE_CODE_VALIDATION=true
ENABLE_PEER_BROADCAST=true
```

### Getting API Keys

1. **Gemini API Key** (Required):
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Set as `GEMINI_API_KEY`

2. **Google Search API** (Optional):
   - Go to [Google Cloud Console](https://console.developers.google.com/)
   - Enable Custom Search API
   - Create credentials (API Key)
   - Set up [Custom Search Engine](https://cse.google.com/)
   - Set `GOOGLE_API_KEY` and `GOOGLE_CSE_ID`

## 🚀 Quick Start

### 1. Interactive Mode
```bash
python src/main.py
```

This starts the interactive AI agent where you can type requests like:
- "What time is it?"
- "Calculate 25 * 4 + 10"
- "Create a tool to convert temperature from Fahrenheit to Celsius"
- "Help me analyze this text for word count"

### 2. API Mode
```bash
python src/tool_api.py
```

Starts a FastAPI server on `http://localhost:8000` with endpoints:
- `GET /` - API status
- `GET /tools` - List available tools
- `POST /execute` - Execute instructions
- `POST /tools/generate` - Generate new tools
- `POST /plan` - Create execution plans

### 3. Demo Mode
```bash
python demo.py
```

Runs a demonstration of the system's capabilities.

## 🧠 How It Works

### 1. Request Analysis
When you make a request, the system:
1. Analyzes your instruction using LLM
2. Determines task type (use existing tools, create new tool, complex workflow)
3. Assesses confidence and required capabilities
4. Creates an execution plan

### 2. Tool Usage
If existing tools can handle the request:
1. Selects appropriate tools
2. Executes them with proper arguments
3. Returns results

### 3. Tool Creation
If new tools are needed:
1. Generates Python code using LLM
2. Validates code for safety and correctness
3. Creates property-based tests
4. Registers the tool if tests pass
5. Broadcasts to peer instances

### 4. Complex Workflows
For complex requests:
1. Breaks down into smaller tasks
2. Creates multi-step execution plan
3. May create new tools as needed
4. Executes plan step by step

## 📚 Examples

### Basic Usage
```python
from planner import intelligent_plan_and_execute

# Use existing tools
results = intelligent_plan_and_execute("What time is it?")

# Trigger tool creation
results = intelligent_plan_and_execute("Convert 100 fahrenheit to celsius")

# Complex workflow
results = intelligent_plan_and_execute("Help me plan a birthday party with cost calculations")
```

### API Usage
```bash
# Execute a request
curl -X POST "http://localhost:8000/execute" \
     -H "Content-Type: application/json" \
     -d '{"instruction": "Calculate the area of a circle with radius 10"}'

# Generate a new tool
curl -X POST "http://localhost:8000/tools/generate" \
     -H "Content-Type: application/json" \
     -d '{"description": "Convert miles to kilometers"}'
```

## 🔧 Architecture

### Core Components

- **`planner.py`**: Intelligent planning and execution engine
- **`agent.py`**: Interactive AI agent with natural language interface
- **`codegen.py`**: LLM-powered code generation with safety validation
- **`registry.py`**: Tool registration and management system
- **`tool_api.py`**: FastAPI web interface
- **`config.py`**: Configuration management
- **`default_tools.py`**: Built-in utility tools

### Supporting Components

- **`testgen.py`**: Property-based test generation
- **`sandbox.py`**: Safe code execution environment
- **`broadcaster.py`**: Peer-to-peer tool sharing
- **`subscriber.py`**: Network listener for tool updates
- **`database.py`**: Persistent storage (if needed)

## 🔒 Safety Features

- **Code Validation**: Checks generated code for dangerous patterns
- **Sandboxed Execution**: Runs generated code in controlled environment
- **Property Testing**: Automatically generates and runs tests
- **Input Validation**: Validates all inputs and parameters
- **Error Handling**: Graceful handling of failures and edge cases

## 🌐 Networking

The system supports peer-to-peer tool sharing:
- Tools created on one instance are automatically shared with others
- Background listener receives new tools from peers
- Configurable broadcast settings

## 🎯 Use Cases

- **Development Assistant**: Generate utility functions and helper tools
- **Data Analysis**: Create custom analysis tools for specific datasets
- **Automation**: Build workflow automation tools on-demand
- **Education**: Interactive tool creation for learning programming
- **Research**: Rapid prototyping of experimental functions
- **Business**: Custom calculations and business logic tools

## 🤝 Contributing

The system is designed to be extensible:

1. **Add Default Tools**: Extend `default_tools.py` with new built-in capabilities
2. **Enhance Planning**: Improve the LLM prompts in `planner.py`
3. **Add Validators**: Extend code validation in `codegen.py`
4. **Create Interfaces**: Build new front-ends using the API

## 📄 License

See LICENSE file for details.

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure `GEMINI_API_KEY` is set correctly
2. **Import Errors**: Check that all dependencies are installed
3. **Tool Creation Fails**: Check internet connection for LLM access
4. **Code Validation**: Adjust safety settings in config if needed

### Debug Mode

Set environment variable for verbose logging:
```bash
export ENABLE_VERBOSE_LOGGING=true
```

### Reset Tools

To clear all tools and start fresh:
```python
from registry import reset_registry
reset_registry()
```

---

**Action Factory** - Where AI meets automation. Create tools as you need them, powered by intelligent planning and code generation.