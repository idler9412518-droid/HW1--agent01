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