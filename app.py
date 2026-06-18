import os
import json
import re
from collections import Counter
from typing import List, Dict, Any, Optional
from litellm import completion

# API key (set here or via environment variable OPENAI_API_KEY)
# os.environ.setdefault("OPENAI_API_KEY", "your-api-key-here")


def generate_response_with_tools(messages: List[Dict], tools: List[Dict]) -> Any:
    """Call LLM with structured tools; returns full response object for tool_calls handling."""
    try:
        response = completion(
            model="openai/gpt-4o",
            messages=messages,
            tools=tools,
            max_tokens=1024,
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Error generating response: {str(e)}")


def analyze_code(code: str) -> dict:
    """
    Analyze Python code and provide feedback.
    """
    try:
        issues = []
        suggestions = []
        score = 100

        if "print(" in code and "logging" not in code:
            issues.append("Uses print() instead of logging")
            suggestions.append("Consider using logging module for better debugging")
            score -= 10

        if "def " in code:
            functions = len(re.findall(r"def\s+\w+", code))
            if functions == 0:
                issues.append("No functions defined")
                score -= 20
        else:
            issues.append("No function definitions found")
            score -= 20

        if '"""' not in code and "'''" not in code:
            issues.append("Missing docstrings")
            suggestions.append("Add docstrings to document your functions")
            score -= 15

        if "try:" not in code and "except" not in code:
            issues.append("No error handling found")
            suggestions.append("Consider adding try-except blocks for robustness")
            score -= 10

        return {
            "status": "success",
            "score": max(0, score),
            "issues": issues,
            "suggestions": suggestions,
            "functions_found": len(re.findall(r"def\s+\w+", code)) if "def " in code else 0,
        }
    except Exception as e:
        return {"status": "error", "error": f"Failed to analyze code: {str(e)}"}


def summarize_text(text: str) -> str:
    """Summarize a given text."""
    try:
        if not text or len(text.strip()) == 0:
            return "Error: Empty text provided"

        sentences = text.split(".")
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= 3:
            return text

        summary_parts = []
        if sentences:
            summary_parts.append(sentences[0])
        if len(sentences) > 2:
            mid = len(sentences) // 2
            summary_parts.append(sentences[mid])
        if len(sentences) > 1:
            summary_parts.append(sentences[-1])

        summary = ". ".join(summary_parts)
        if not summary.endswith("."):
            summary += "."

        return f"Summary: {summary}"
    except Exception as e:
        return f"Error summarizing text: {str(e)}"


def add_task(task: str) -> dict:
    """Add a task to the task list."""
    try:
        if not task or len(task.strip()) == 0:
            return {"status": "error", "message": "Empty task provided"}

        if not hasattr(add_task, "task_list"):
            add_task.task_list = []

        task_id = len(add_task.task_list) + 1
        task_item = {"id": task_id, "task": task.strip(), "status": "pending"}
        add_task.task_list.append(task_item)

        return {
            "status": "success",
            "message": "Task added successfully",
            "task_id": task_id,
            "task": task_item,
            "total_tasks": len(add_task.task_list),
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to add task: {str(e)}"}


def list_files() -> List[str]:
    """List all files in the current directory."""
    try:
        return [f for f in os.listdir(".") if os.path.isfile(f)]
    except Exception as e:
        return [f"Error listing files: {str(e)}"]


def read_file(file_name: str) -> str:
    """Read the content of a file."""
    try:
        if not os.path.exists(file_name):
            return f"Error: File '{file_name}' not found"
        with open(file_name, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def terminate(message: str) -> dict:
    """End the agent loop and print a summary to the user."""
    return {"status": "terminate", "message": message or "Agent terminated."}


def analyze_text(
    text: str,
    language: str = "en",
    detailed: bool = False,
) -> dict:
    """
    Analyze text for sentiment and keywords.
    Uses multiple parameters: string, enum, and boolean.
    """
    try:
        if not text or not text.strip():
            return {"status": "error", "message": "Empty text provided"}

        # Simple keyword extraction (words longer than 4 chars, excluding common stop words)
        stop = {"that", "this", "with", "from", "have", "were", "been", "would", "could", "their", "there", "which"}
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        keywords = [w for w in words if w not in stop]
        # Count and return top keywords
        counts = Counter(keywords)
        top_keywords = [k for k, _ in counts.most_common(10)]

        # Simple sentiment: count positive/negative words (very basic)
        positive = {"good", "great", "excellent", "happy", "love", "best", "nice", "positive", "success"}
        negative = {"bad", "poor", "terrible", "sad", "hate", "worst", "wrong", "negative", "fail"}
        pos_count = sum(1 for w in words if w in positive)
        neg_count = sum(1 for w in words if w in negative)
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        result = {
            "status": "success",
            "sentiment": sentiment,
            "keywords": top_keywords,
            "language_requested": language,
        }
        if detailed:
            result["word_count"] = len(words)
            result["positive_indicators"] = pos_count
            result["negative_indicators"] = neg_count
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Map tool names to functions for execution
tool_functions = {
    "analyze_code": analyze_code,
    "summarize_text": summarize_text,
    "add_task": add_task,
    "list_files": list_files,
    "read_file": read_file,
    "terminate": terminate,
    "analyze_text": analyze_text,
}

# Structured tool definitions (JSON Schema) for LLM-native function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_code",
            "description": "Analyze Python code and provide feedback, suggestions, and a quality score.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The Python code string to analyze"},
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_text",
            "description": "Create a concise summary of the given text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to summarize"},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a task to the in-memory task list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Description of the task to add"},
                },
                "required": ["task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List all files in the current directory.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the content of a specified file in the directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {"type": "string", "description": "Name of the file to read"},
                },
                "required": ["file_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "terminate",
            "description": "End the agent loop and print a summary message to the user. Use when the task is complete or to say goodbye.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Summary or farewell message to show the user"},
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_text",
            "description": "Analyze text for sentiment and keywords. Supports optional language hint and detailed output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to analyze"},
                    "language": {
                        "type": "string",
                        "enum": ["en", "es", "fr"],
                        "description": "Language code for the text (en=English, es=Spanish, fr=French)",
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "If true, include word count and sentiment indicators in the result",
                        "default": False,
                    },
                },
                "required": ["text"],
            },
        },
    },
]

agent_rules = [
    {
        "role": "system",
        "content": """
You are an AI agent that can perform tasks by using available tools.

Your purpose is to be a helpful coding assistant that can:
- Review and analyze code (analyze_code)
- Summarize text and analyze sentiment/keywords (summarize_text, analyze_text)
- Manage tasks (add_task)
- Work with files (list_files, read_file)

Guidelines:
- If a user asks about files or file content, list files before reading when appropriate.
- Always provide helpful and constructive feedback.
- When you have finished helping the user or want to respond with a final message, use the terminate tool with your message.
""",
    }
]


def validate_tool_args(tool_name: str, args: Dict[str, Any]) -> Optional[str]:
    """Validate that required arguments are present and non-empty. Returns error message or None."""
    if tool_name not in tool_functions:
        return f"Unknown tool: {tool_name}"

    schema = next(
        (t["function"] for t in tools if t["function"]["name"] == tool_name),
        None,
    )
    if not schema:
        return f"No schema for tool: {tool_name}"

    required = schema.get("parameters", {}).get("required", [])
    for key in required:
        if key not in args:
            return f"Missing required argument: {key}"
        val = args[key]
        if val is None or (isinstance(val, str) and not val.strip()):
            return f"Argument '{key}' must be non-empty"
    return None


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute a tool by name with validated arguments. Returns result or error dict."""
    if tool_name not in tool_functions:
        return {"error": f"Unknown tool: {tool_name}"}

    err = validate_tool_args(tool_name, arguments)
    if err:
        return {"error": err}

    try:
        fn = tool_functions[tool_name]
        result = fn(**arguments)
        return {"result": result}
    except TypeError as e:
        return {"error": f"Invalid arguments for {tool_name}: {str(e)}"}
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}


def _get_tool_call_field(tool_call: Any, field_path: str) -> Any:
    """Get a field from a tool call, whether it's an object or a dict (LiteLLM can return either)."""
    if tool_call is None:
        return None
    parts = field_path.split(".")
    obj = tool_call
    for part in parts:
        if obj is None:
            return None
        obj = obj.get(part) if isinstance(obj, dict) else getattr(obj, part, None)
    return obj


def parse_tool_call_arguments(tool_call: Any) -> Dict[str, Any]:
    """
    Parse the arguments from a single tool call. The LLM API returns tool_calls with
    function.arguments as a JSON string (OpenAI/LiteLLM spec); this is the only place
    we decode that. We do not parse assistant message content as JSON—only native
    tool_calls from the response are used.
    """
    raw = _get_tool_call_field(tool_call, "function.arguments")
    if not raw or not isinstance(raw, str):
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def run_agent():
    """
    Main agent loop using the LLM's built-in tool-calling API only.
    We do not parse assistant message content as JSON; all tool invocations
    come from response.message.tool_calls (OpenAI/LiteLLM standard).
    """
    print("=" * 60)
    print("Agentic AI Application - Coding Assistant (Structured Tools)")
    print("=" * 60)
    print("\nAvailable commands:")
    print('  - Type your request (e.g., "analyze this code: def hello(): print(\\"hi\\")")')
    print("  - Type 'quit' or 'exit' to terminate")
    print("=" * 60)

    memory = [dict(m) for m in agent_rules]
    iterations = 0
    max_iterations = 50

    while iterations < max_iterations:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "stop"]:
                print("\nAgent: Goodbye! Thank you for using the agentic AI application.")
                break

            memory.append({"role": "user", "content": user_input})

            # Use only the LLM's built-in tool_calls—we never parse assistant content as JSON.
            # Loop: allow multiple tool calls per turn until LLM responds without tool_calls or terminates
            while True:
                print("\nAgent thinking...")
                try:
                    response = generate_response_with_tools(memory, tools)
                except RuntimeError as e:
                    print(f"\nAgent: {e}")
                    break

                message = response.choices[0].message
                content = getattr(message, "content", None) or ""
                tool_calls = getattr(message, "tool_calls", None) or []

                # No tool calls: show content and wait for next user input
                if not tool_calls:
                    if content:
                        print(f"\nAgent: {content}")
                    else:
                        print("\nAgent: (No response content.)")
                    break

                # Build assistant message with tool_calls for history (OpenAI/LiteLLM format)
                assistant_msg = {"role": "assistant", "content": content or None, "tool_calls": []}
                for tc in tool_calls:
                    tc_id = _get_tool_call_field(tc, "id")
                    fn_name = _get_tool_call_field(tc, "function.name")
                    fn_args = _get_tool_call_field(tc, "function.arguments")
                    assistant_msg["tool_calls"].append(
                        {
                            "id": tc_id,
                            "type": "function",
                            "function": {"name": fn_name, "arguments": fn_args or ""},
                        }
                    )
                memory.append(assistant_msg)

                # Execute each tool call using parsed arguments (from native tool_calls only)
                for tc in tool_calls:
                    tool_name = _get_tool_call_field(tc, "function.name") or ""
                    tool_args = parse_tool_call_arguments(tc)
                    tc_id = _get_tool_call_field(tc, "id")

                    result = execute_tool(tool_name, tool_args)
                    result_str = json.dumps(result)

                    # Handle terminate: print message and exit agent loop
                    if tool_name == "terminate" and "result" in result:
                        msg = (result["result"] or {}).get("message", "Goodbye.")
                        print(f"\nAgent: {msg}")
                        return

                    print(f"\nTool: {tool_name} -> {result_str}")

                    # Append tool result for OpenAI/LiteLLM format
                    memory.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc_id,
                            "content": result_str,
                        }
                    )

                iterations += 1
                if iterations >= max_iterations:
                    print("\nAgent: Maximum iterations reached. Terminating.")
                    return

        except KeyboardInterrupt:
            print("\n\nAgent: Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\nError in agent loop: {str(e)}")
            memory.append({"role": "assistant", "content": f"Error occurred: {str(e)}"})
            iterations += 1

    if iterations >= max_iterations:
        print("\nAgent: Maximum iterations reached. Terminating.")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set in environment variables.")
        print("Set it with: $env:OPENAI_API_KEY = 'your-key' (PowerShell)")
        print("         or: export OPENAI_API_KEY='your-key' (Linux/Mac)")
        print("\nProceeding anyway... (will fail if API key is required)\n")
    run_agent()
