# main.py
import argparse
import json
import sys
import os

from dotenv import load_dotenv

# 加载 .env（如果存在）
load_dotenv()

from agent import CodeReviewAgent


def check_env():
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("错误: 未设置 DASHSCOPE_API_KEY。请在 .env 中配置或 export 环境变量。")
        sys.exit(1)


def print_pretty(raw_json: str):
    """尽量美化输出；如果不是合法 JSON，原样打印。"""
    try:
        data = json.loads(raw_json)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print(raw_json)


def main():
    parser = argparse.ArgumentParser(description="通义千问代码审查 Agent")
    parser.add_argument("--file", "-f", help="要审查的文件路径，例如 demo.py")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="进入交互式多轮模式"
    )
    args = parser.parse_args()

    check_env()
    agent = CodeReviewAgent()

    if args.file:
        prompt = f"请审查文件 {args.file}，先读取文件内容，必要时运行静态检查，然后给出结构化审查结果。"
        raw = agent.run(prompt)
        print_pretty(raw)
        return

    if args.interactive or not args.file:
        print("千问代码审查 Agent（输入 exit 退出，输入 reset 清空上下文）")
        print("示例: 请审查 demo.py\n")
        while True:
            try:
                user_input = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见。")
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                break
            if user_input.lower() == "reset":
                agent.reset()
                print("上下文已清空。")
                continue

            raw = agent.run(user_input)
            print_pretty(raw)
            print()


if __name__ == "__main__":
    main()