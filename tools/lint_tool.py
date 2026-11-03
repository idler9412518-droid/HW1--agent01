# tools/lint_tool.py
import subprocess
import sys


def run_static_check(path: str) -> dict:
    """调用 ruff 做静态检查，返回结构化问题列表。"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", path, "--output-format=json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return {"error": "静态检查超时（15s）"}
    except FileNotFoundError:
        return {"error": "ruff 未安装，请执行: pip install ruff"}

    import json
    try:
        issues = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        return {"error": f"无法解析 ruff 输出: {result.stdout[:500]}"}

    simplified = [
        {
            "line": item.get("location", {}).get("row"),
            "code": item.get("code"),
            "message": item.get("message"),
        }
        for item in issues
    ]
    return {"source": "ruff", "issue_count": len(simplified), "issues": simplified}