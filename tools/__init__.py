# tools/__init__.py
from .file_tool import read_file
from .lint_tool import run_static_check

# 白名单注册表：只有这里注册的工具才允许被模型调用
TOOL_REGISTRY = {
    "read_file": read_file,
    "run_static_check": run_static_check,
}

# 给模型看的工具声明（JSON Schema）
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地代码文件的内容。需要审查某个文件时先调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径"}
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_static_check",
            "description": "对 Python 文件运行 ruff 静态检查，返回语法错误、未定义名称等问题列表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Python 文件路径"}
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
]