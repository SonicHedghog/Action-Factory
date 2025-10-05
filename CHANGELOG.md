# Action Factory v2.0 - LLM-Powered Tool Creation System

## 🎯 Project Summary

This project has been completely rewritten to use Large Language Models (LLMs) for intelligent planning and automatic tool creation. The system now analyzes user requests, determines the best approach, and can create new tools on-demand.

## 🚀 Key Improvements

### 1. Intelligent Planning Engine (`planner.py`)
- **LLM-Powered Analysis**: Uses Google Gemini to understand user intent
- **Task Classification**: Automatically categorizes requests as:
  - Use existing tools
  - Create new tool
  - Complex multi-step workflow
  - Request clarification
- **Execution Planning**: Creates step-by-step plans to accomplish goals
- **Tool Creation**: Automatically generates, tests, and registers new tools

### 2. Enhanced Agent System (`agent.py`)
- **Natural Language Interface**: Conversational AI that understands context
- **Intelligent Response Generation**: Creates helpful, user-friendly responses
- **Interactive Commands**: Built-in help, status, and reset commands
- **Error Handling**: Graceful handling of failures with user guidance

### 3. Advanced Code Generation (`codegen.py`)
- **Context-Aware Generation**: Considers existing tools to avoid duplication
- **Safety Validation**: Checks for dangerous patterns and malicious code
- **Comprehensive Documentation**: Generates well-documented, production-ready code
- **Type Hints**: Full type annotation support

### 4. Rich Default Tools (`default_tools.py`)
- **Mathematical Operations**: Safe expression evaluation
- **Text Analysis**: Word counts, statistics, and analysis
- **Time/Date Functions**: Current time with formatting
- **Random Generation**: Numbers, passwords, secure data
- **Data Validation**: JSON formatting, URL validation
- **Web Search**: Google search integration (with API key)

### 5. Configuration Management (`config.py`)
- **Environment Variables**: Comprehensive configuration via .env
- **Validation**: Automatic config validation with helpful error messages
- **LLM Settings**: Configurable temperature and model settings
- **Safety Controls**: Toggleable security and validation features

### 6. Enhanced API (`tool_api.py`)
- **RESTful Endpoints**: Full API for tool management and execution
- **Interactive Documentation**: FastAPI with automatic OpenAPI docs
- **Tool Generation**: API endpoints for creating tools programmatically
- **Status Monitoring**: Real-time system status and tool inventory

## 🔧 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Request   │───▶│  LLM Planner    │───▶│  Execution      │
│                 │    │  (Analysis)     │    │  Engine         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Tool Registry  │    │  Code Generator │
                       │  (Existing)     │    │  (New Tools)    │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Tool Executor  │    │  Validator &    │
                       │                 │    │  Tester         │
                       └─────────────────┘    └─────────────────┘
```

## 🎯 Usage Examples

### Interactive Mode
```bash
python src/main.py
```

Example interactions:
- **"What time is it?"** → Uses existing `current_time` tool
- **"Convert 100 fahrenheit to celsius"** → Creates new temperature conversion tool
- **"Help me calculate compound interest"** → Creates financial calculation tool
- **"Analyze this text for readability"** → Uses existing text analysis or creates new tool

### API Mode
```bash
curl -X POST "http://localhost:8000/execute" \
     -H "Content-Type: application/json" \
     -d '{"instruction": "Create a tool to calculate BMI and use it for height 180cm, weight 75kg"}'
```

### Programmatic Usage
```python
from planner import intelligent_plan_and_execute

results = intelligent_plan_and_execute("Help me plan a dinner party for 8 people")
```

## 🔒 Safety Features

1. **Code Validation**: Scans generated code for dangerous patterns
2. **Sandboxed Testing**: Property-based testing before tool registration
3. **Input Sanitization**: Validates all user inputs and parameters
4. **Safe Execution**: Controlled execution environment for generated code
5. **Error Boundaries**: Graceful degradation when things go wrong

## 📊 System Capabilities

### Automatic Tool Creation
The system can create tools for:
- Mathematical calculations
- Data conversions
- Text processing
- File operations (safe)
- API integrations
- Business logic
- Scientific calculations
- And much more!

### Planning Intelligence
- Understands complex, multi-part requests
- Breaks down large tasks into manageable steps
- Reuses existing tools when possible
- Creates new tools only when necessary
- Provides explanations for its decisions

### Learning and Adaptation
- Remembers created tools for future use
- Shares tools across multiple instances
- Improves with usage patterns
- Adapts to user preferences

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Run Basic Tests**:
   ```bash
   python test_basic.py
   ```

4. **Start the System**:
   ```bash
   python src/main.py
   ```

5. **Try the Demo**:
   ```bash
   python demo.py
   ```

## 🎉 Benefits

- **Productivity**: Create tools on-demand without manual programming
- **Flexibility**: Handles a wide variety of requests intelligently
- **Safety**: Multiple layers of validation and security
- **Scalability**: Share tools across multiple instances
- **Extensibility**: Easy to add new capabilities and default tools
- **User-Friendly**: Natural language interface with helpful guidance

The Action Factory is now a true AI-powered automation platform that can understand what you need and create the tools to accomplish it!