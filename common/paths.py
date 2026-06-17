"""项目根目录与路径工具，消除对当前工作目录（CWD）的依赖。"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def project_path(*parts: str) -> Path:
    """返回项目根目录下的绝对路径。

    用法：project_path("config", "config.yaml")
    """
    return PROJECT_ROOT.joinpath(*parts)
