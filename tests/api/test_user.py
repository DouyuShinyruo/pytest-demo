# tests/api/test_user.py
import pytest
from common.data_loader import load_yaml

pytestmark = pytest.mark.api


def test_create_user_success(api_client, base_url):
    """测试创建用户成功"""
    resp = api_client.post(
        f"{base_url}/api/users",
        json={"name": "张三", "email": "zhangsan@example.com"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "张三"
    assert data["email"] == "zhangsan@example.com"
    assert "id" in data


def test_create_user_empty_name(api_client, base_url):
    """测试创建用户-用户名为空"""
    resp = api_client.post(
        f"{base_url}/api/users",
        json={"name": ""},
    )
    assert resp.status_code == 400


def test_get_user_list(api_client, base_url):
    """测试获取用户列表"""
    # 先创建一个用户
    api_client.post(f"{base_url}/api/users", json={"name": "张三"})
    # 获取列表
    resp = api_client.get(f"{base_url}/api/users")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1


def test_get_user_not_found(api_client, base_url):
    """测试获取不存在的用户"""
    resp = api_client.get(f"{base_url}/api/users/999")
    assert resp.status_code == 404


def test_update_user(api_client, base_url):
    """测试更新用户"""
    # 先创建
    create_resp = api_client.post(
        f"{base_url}/api/users", json={"name": "张三"}
    )
    user_id = create_resp.json()["id"]
    # 更新
    resp = api_client.put(
        f"{base_url}/api/users/{user_id}",
        json={"name": "李四"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "李四"


def test_delete_user(api_client, base_url):
    """测试删除用户"""
    # 先创建
    create_resp = api_client.post(
        f"{base_url}/api/users", json={"name": "张三"}
    )
    user_id = create_resp.json()["id"]
    # 删除
    resp = api_client.delete(f"{base_url}/api/users/{user_id}")
    assert resp.status_code == 200
    # 确认已删除
    get_resp = api_client.get(f"{base_url}/api/users/{user_id}")
    assert get_resp.status_code == 404


# YAML 数据驱动测试
yaml_cases = load_yaml("test_data/api/user.yaml")


@pytest.mark.parametrize(
    "case",
    yaml_cases,
    ids=[c["name"] for c in yaml_cases],
)
def test_api_from_yaml(api_client, base_url, case):
    """YAML 数据驱动测试"""
    method = case["method"].upper()
    url = f"{base_url}{case['path']}"

    if method == "GET":
        resp = api_client.get(url)
    elif method == "POST":
        resp = api_client.post(url, json=case.get("body"))
    elif method == "PUT":
        resp = api_client.put(url, json=case.get("body"))
    elif method == "DELETE":
        resp = api_client.delete(url)
    else:
        raise ValueError(f"不支持的 HTTP 方法: {method}")

    assert resp.status_code == case["expected_status"]

    if "expected_fields" in case:
        data = resp.json()
        for field in case["expected_fields"]:
            assert field in data
