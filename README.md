代码审查agent
使用示例：python main.py --file example/demo.py

demo.py
{
# 错误示例

import os


def divide(a, b):
    return a / b          # 没有处理 b=0


def read_config(path):
    f = open(path)        # 没有使用 with，文件可能不关闭
    return f.read()


def get_user(users, name):
    for u in users:
        if u["name"] == name:
            return u
    # 没有处理找不到用户的情况，隐式返回 None


API_KEY = "sk-hardcoded-secret-123456"   # 硬编码密钥


def main():
    print(divide(10, 0))  # 必然除零
    print(read_config("config.json"))


if __name__ == "__main__":
    main()
}



终端输出：

{
  "summary": "该文件存在多个严重问题：未处理除零异常、文件未使用上下文管理器导致资源泄漏、未处理查找失败的边界情况、硬编码敏感密钥，以及未使用的导入。静态检查也报告了未使用 import 和不推荐的文件打开方式。",
  "verdict": "request_changes",
  "issues": [
    {
      "severity": "high",
      "line": 5,
      "type": "bug",
      "description": "函数 `divide` 未检查除数 `b` 是否为零，调用 `divide(10, 0)` 将触发 ZeroDivisionError。",
      "suggestion": "添加 `if b == 0: raise ValueError('Division by zero')` 或返回默认值/使用try-except 处理。"
    },
    {
      "severity": "high",
      "line": 9,
      "type": "bug",
      "description": "`read_config` 直接使用 `open()` 而未用 `with` 语句，若读取过程中异常，文件句柄可能无法关闭，造成资源泄漏。",
      "suggestion": "改用 `with open(path) as f: return f.read()`。"
    },
    {
      "severity": "high",
      "line": 15,
      "type": "bug",
      "description": "`get_user` 在循环未匹配时隐式返回 `None`，调用方可能因 `None` 导致 AttributeError（如 `u['id']`），缺乏明确错误处理。",
      "suggestion": "在循环后添加 `raise KeyError(f'User {name} not found')` 或返回 `None` 并在文档中明确说明，推荐显式抛异常。"
    },
    {
      "severity": "high",
      "line": 18,
      "type": "security",
      "description": "API_KEY 硬编码在源码中，属于严重安全风险，易被泄露。",
      "suggestion": "应从环境变量读取，例如 `os.getenv('API_KEY')`，并确保 `.env` 文件不提交至版本控制。"
    },
    {
      "severity": "medium",
      "line": 3,
      "type": "style",
      "description": "导入 `os` 模块但未使用，违反 PEP 8 且增加维护负担。",
      "suggestion": "删除 `import os`。"
    },
    {
      "severity": "medium",
      "line": 9,
      "type": "style",
      "description": "ruff 报告 `SIM115`: 应使用上下文管理器打开文件，与前述 bug 一致，属最佳实践缺失。",
      "suggestion": "同上，改用 `with open(path) as f:`。"
    }
  ],
  "improved_code": "def divide(a, b):\n    if b == 0:\n        raise ValueError('Division by zero')\n    return a / b\n\n\ndef read_config(path):\n    with open(path) as f:\n        return f.read()\n\n\ndef get_user(users, name):\n    for u in users:\n        if u[\"name\"] == name:\n            return u\n    raise KeyError(f'User {name} not found')\n\n\nimport os\nAPI_KEY= os.getenv('API_KEY', '')  # 从环境变量读取\n\n\ndef main():\n    try:\n        print(divide(10, 0))\n    except ValueError as e:\n        print(f'Error: {e}')\n    print(read_config(\"config.json\"))\n\n\nif __name__ == \"__main__\":\n    main()"
}
