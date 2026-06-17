# conftest.py
import pytest
from common.config import Config
from common.logger import get_logger


@pytest.fixture(scope="session")
def config():
    """全局配置 fixture"""
    return Config()


@pytest.fixture(scope="session")
def logger():
    """全局日志 fixture"""
    return get_logger("pytest")
