# tests/test_data_loader.py
from common.data_loader import load_yaml


def test_load_yaml():
    """测试加载 YAML 文件"""
    data = load_yaml("test_data/api/user.yaml")
    assert isinstance(data, list)
    assert len(data) > 0


def test_yaml_has_required_fields():
    """测试 YAML 数据包含必要字段"""
    data = load_yaml("test_data/api/user.yaml")
    for case in data:
        assert "name" in case
        assert "method" in case
        assert "path" in case
