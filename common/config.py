# common/config.py
import yaml
from pathlib import Path

from common.paths import PROJECT_ROOT


class Config:
    def __init__(self, config_path="config/config.yaml"):
        # 相对路径按项目根解析，避免依赖当前工作目录
        path = Path(config_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        with open(path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    def get(self, key, default=None):
        """支持点号分隔的嵌套 key，如 'api.base_url'"""
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
