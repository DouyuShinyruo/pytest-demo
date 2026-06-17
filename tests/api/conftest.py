# tests/api/conftest.py
import pytest
import requests

from common.process_utils import start_service


@pytest.fixture(scope="session")
def mock_server(config):
    """启动 Mock API 服务，测试结束后关闭"""
    proc = start_service(
        "mock_services.api_mock",
        "127.0.0.1",
        5000,
    )
    yield proc
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="function")
def api_client(config, mock_server):
    """API 测试客户端，每个测试前重置数据"""
    base_url = config.get("api.base_url")
    client = requests.Session()
    client.base_url = base_url

    # 每个测试前重置数据
    client.post(f"{base_url}/api/reset")

    yield client

    client.close()


@pytest.fixture
def base_url(api_client):
    """获取 base_url"""
    return api_client.base_url
