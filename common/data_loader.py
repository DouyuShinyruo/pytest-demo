# common/data_loader.py
import yaml


def load_yaml(file_path):
    """加载 YAML 测试数据文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
