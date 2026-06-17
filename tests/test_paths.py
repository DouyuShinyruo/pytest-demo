from pathlib import Path
from common.paths import PROJECT_ROOT, project_path


def test_project_root_is_absolute_dir():
    """PROJECT_ROOT 必须是存在的绝对目录"""
    assert PROJECT_ROOT.is_absolute()
    assert PROJECT_ROOT.is_dir()


def test_project_root_contains_known_files():
    """项目根下应包含 pytest.ini 与 common/ 目录"""
    assert (PROJECT_ROOT / "pytest.ini").is_file()
    assert (PROJECT_ROOT / "common").is_dir()


def test_project_path_joins_parts():
    """project_path 拼接相对路径片段"""
    p = project_path("config", "config.yaml")
    assert p == PROJECT_ROOT / "config" / "config.yaml"
    assert isinstance(p, Path)
