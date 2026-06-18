# Agentic AI Application

A modular AI agent that performs tasks using a set of tools. This application demonstrates concepts from prompting, memory management, agent loops, and behavior definition to create a functional AI agent.

## Table of Contents

- [What It Does](#what-it-does)
- [Features](#features)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [Architecture](#architecture)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

## What It Does

This agentic AI application is a coding assistant that can:

- Analyze Python code - Review code quality, identify issues, and provide suggestions
- Summarize text - Create concise summaries of long text passages
- Manage tasks - Add and track tasks in a task list
- Work with files - List and read files from the current directory
- Maintain context - Remember previous conversations and interactions

The agent uses an LLM (Language Model) to understand natural language requests, parse them into structured actions, and execute appropriate tools to complete tasks.

## Features

- Agent Loop - Continuous interaction with iterative tool execution
- Memory Management - Maintains conversation history for context-aware responses
- Modular Tools - Extensible tool system with 5+ available tools
- Structured Responses - Parses LLM responses into executable actions
- Error Handling - Graceful handling of invalid inputs and tool errors
- Interactive CLI - User-friendly command-line interface

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenAI API key (or compatible LLM provider)

### Step 1: Clone or Download

```bash
# If using git
git clone <repository-url>
cd agenticAI_ass1

# Or simply download the files
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `litellm` - For LLM API interactions

## Setup

### Option 1: Environment Variable (Recommended)

Set your OpenAI API key as an environment variable:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY = "your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Option 2: Direct in Code

Edit `app.py` and set the API key at the top of the file:

```python
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

**Warning:** Don't commit API keys to version control!

## Usage

### Basic Usage

Run the application:

```bash
python app.py
```

### Interactive Commands

Once running, you can interact with the agent using natural language:

```
You: Can you analyze this code: def hello(): print("hi")

Agent: [Processes request and analyzes code]

You: Now summarize the analysis

Agent: [Summarizes the previous analysis]
```

### Exit Commands

Type any of the following to exit:
- `quit`
- `exit`
- `stop`
- Or press `Ctrl+C`

## Available Tools

### Custom Tools

1. **`analyze_code(code: str)`** → `dict`
   - Analyzes Python code for quality issues
   - Returns score, issues, and suggestions
   - Checks for docstrings, error handling, and best practices

2. **`summarize_text(text: str)`** → `str`
   - Creates concise summaries of text
   - Extracts key sentences and main points
   - Useful for condensing long content

3. **`add_task(task: str)`** → `dict`
   - Adds tasks to an in-memory task list
   - Returns task ID and status
   - Tracks total number of tasks

### Standard Tools

4. **`list_files()`** → `List[str]`
   - Lists all files in the current directory
   - Returns array of file names

5. **`read_file(file_name: str)`** → `str`
   - Reads and returns file contents
   - Handles file not found errors

6. **`terminate(message: str)`**
   - Ends the agent loop
   - Prints a summary message

## Architecture

### Components

1. **Prompting Agent** (`generate_response`)
   - Interfaces with LLM via litellm
   - Handles API calls and error management

2. **Memory Management**
   - Maintains conversation history
   - Appends user/assistant messages
   - Preserves context across interactions

3. **Agent Loop** (`run_agent`)
   - Main interaction loop
   - Processes user input
   - Executes tools based on parsed actions
   - Updates memory after each iteration

4. **Behavior Definition** (`agent_rules`)
   - System instructions for the agent
   - Defines available tools and guidelines
   - Specifies response format requirements

5. **Response Parsing** (`parse_action`)
   - Extracts structured actions from LLM responses
   - Handles JSON parsing and validation
   - Manages error cases

### Flow Diagram

```
User Input → Memory Update → LLM Call → Parse Response → Execute Tool → Update Memory → Repeat
```

## Examples

### Example 1: Code Analysis

```
You: Analyze this code: def calculate(x, y): return x + y

Agent: [Calls analyze_code tool]
Action result: {
  "result": {
    "status": "success",
    "score": 75,
    "issues": ["Missing docstrings", "No error handling found"],
    "suggestions": ["Add docstrings to document your functions", ...]
  }
}
```

### Example 2: Task Management

```
You: Add a task to review the documentation

Agent: [Calls add_task tool]
Action result: {
  "result": {
    "status": "success",
    "task_id": 1,
    "task": {"id": 1, "task": "review the documentation", "status": "pending"},
    "total_tasks": 1
  }
}
```

### Example 3: File Operations

```
You: What files are in this directory?

Agent: [Calls list_files tool]
Action result: {
  "result": ["agentic_ai_app.py", "requirements.txt", "README.md"]
}

You: Read the README file

Agent: [Calls read_file tool]
Action result: {
  "result": "[File contents...]"
}
```

### Example 4: Memory Demonstration

```
You: My name is Alice

Agent: [Stores in memory]

You: What's my name?

Agent: [References previous conversation]
Your name is Alice.
```

## Troubleshooting

### API Key Issues

**Problem:** `Error generating response: Invalid API key`

**Solution:**
- Verify your API key is correct
- Check environment variable is set: `echo $OPENAI_API_KEY` (Linux/Mac) or `echo %OPENAI_API_KEY%` (Windows)
- Ensure the key has proper permissions

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'litellm'`

**Solution:**
```bash
pip install --upgrade litellm
```

### JSON Parsing Errors

**Problem:** `Invalid JSON response`

**Solution:**
- The agent will handle this automatically
- If persistent, check your LLM provider's response format
- Ensure you're using a compatible model (gpt-4o recommended)

### Maximum Iterations Reached

**Problem:** Agent stops after 50 iterations

**Solution:**
- This is a safety limit
- Modify `max_iterations` in `run_agent()` if needed
- Or use the `terminate` tool to end gracefully

## Project Structure

```
agenticAI_ass1/
├── app.py               # Main application file
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Resources

- [JSON Schema Official Docs](https://json-schema.org/learn) – Standard way to describe tool parameters and types
- [LiteLLM Tool Calling Guide](https://docs.litellm.ai/docs/completion/function_call) – Function/tool calling with LiteLLM
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling) – OpenAI function-calling API reference

## Learning Objectives

This project demonstrates:

- Prompting techniques for LLM interaction
- Memory management in conversational AI
- Agent loop implementation
- Tool-based agent architecture
- Response parsing and action execution
- Error handling in AI systems

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, please refer to the assignment documentation or contact your instructor.
