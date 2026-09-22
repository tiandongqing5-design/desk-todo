"""desk-todo —— 把「今日待办」画在桌面背景上的待办事项管理器。

包的对外入口：
    python -m desktodo.cli        # 命令行
    python -m desktodo.web.app    # 浏览器界面

数据读写统一走 ``desktodo.storage``，不要绕开它直接碰 JSON 文件。
"""

__version__ = "0.1.0"
__all__ = ["__version__"]
