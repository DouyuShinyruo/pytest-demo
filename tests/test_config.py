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
