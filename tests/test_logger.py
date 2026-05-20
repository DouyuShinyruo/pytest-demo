import logging
from common.logger import get_logger


def test_get_logger():
    """测试获取 logger 实例"""
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test"


def test_logger_has_handler():
    """测试 logger 有处理器"""
    logger = get_logger("test_handler")
    assert len(logger.handlers) > 0
