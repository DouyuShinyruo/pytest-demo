# tests/api/conftest.py
import pytest
import requests

# mock_server 已上提到根 conftest.py 作为 session 级全局共享服务（端口 5000），
# 避免与 step_defs/、性能测试争抢同一端口。


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
