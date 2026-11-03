# tools/file_tool.py
import os


def read_file(path: str) -> dict:
    """读取代码文件，返回内容与元信息。"""
    if not os.path.exists(path):
        return {"error": f"文件不存在: {path}"}

    if os.path.getsize(path) > 200_000:
        return {"error": "文件超过 200KB，请分段审查或指定更小的文件。"}

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return {"error": f"无法以文本方式读取（可能是二进制文件）: {path}"}

    return {
        "path": path,
        "lines": len(content.splitlines()),
        "content": content,
    }