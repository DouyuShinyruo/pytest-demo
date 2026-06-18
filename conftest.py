# conftest.py
import subprocess

import pytest
from common.config import Config
from common.logger import get_logger
from common.process_utils import start_service


def _stop_service(proc):
    """可靠关闭服务进程：先 terminate，超时则 kill，杜绝孤儿进程。"""
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


@pytest.fixture(scope="session")
def config():
    """全局配置 fixture"""
    return Config()


@pytest.fixture(scope="session")
def logger():
    """全局日志 fixture"""
    return get_logger("pytest")


@pytest.fixture(scope="session")
def mock_server():
    """全局唯一 Mock API 服务（端口 5000）。

    session 级共享：tests/api 与 step_defs/api 的测试、以及性能测试都复用
    同一实例，避免多个服务争抢同一端口（这是过去全量套件偶发挂起的根因）。
    """
    proc = start_service(
        "mock_services.api_mock",
        "127.0.0.1",
        5000,
    )
    yield proc
    _stop_service(proc)


@pytest.fixture(scope="session")
def web_server():
    """全局唯一 Mock Web 服务（端口 8080），session 级共享。"""
    proc = start_service(
        "mock_services.web_mock",
        "127.0.0.1",
        8080,
    )
    yield proc
    _stop_service(proc)

