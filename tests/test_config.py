import os
import pytest
from common.config import Config


def test_load_config():
    """测试配置文件加载"""
    config = Config("config/config.yaml")
    assert config.get("env") == "test"


def test_get_nested_value():
    """测试获取嵌套配置"""
    config = Config("config/config.yaml")
    assert config.get("api.base_url") == "http://localhost:5000"


def test_get_with_default():
    """测试默认值"""
    config = Config("config/config.yaml")
    assert config.get("not_exist", "default") == "default"


import os
from common.paths import PROJECT_ROOT


def test_config_loads_after_chdir():
    """切换到非项目目录后，Config 仍能加载配置（无 CWD 依赖）"""
    cwd_before = os.getcwd()
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))  # 切到 tests/
        config = Config()  # 走默认路径，必须能找到 config/config.yaml
        assert config.get("env") == "test"
        assert config.get("api.base_url") == "http://localhost:5000"
    finally:
        os.chdir(cwd_before)


def test_config_explicit_relative_path_resolved():
    """显式传相对路径时，按项目根解析而非 CWD"""
    cwd_before = os.getcwd()
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        config = Config("config/config.yaml")
        assert config.get("protocol.port") == 9000
    finally:
        os.chdir(cwd_before)
