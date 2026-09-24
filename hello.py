"""desk-todo 的第一个脚本：验证环境与命令行参数。

用法：
    python hello.py            → 你好，世界！
    python hello.py 小明       → 你好，小明！
"""

import sys


def greeting(name: str = "世界") -> str:
    """拼一句问候语。

    参数 name 有默认值 "世界"，所以 greeting() 和 greeting("小明") 都能调用。
    """
    return f"你好，{name}！desk-todo 已就绪。"


if __name__ == "__main__":
    # sys.argv 是命令行参数列表，第 0 项永远是脚本名本身，
    # 所以真正传入的参数从第 1 项开始。没传参数时退回默认值。
    who = sys.argv[1] if len(sys.argv) > 1 else "世界"
    print(greeting(who))
