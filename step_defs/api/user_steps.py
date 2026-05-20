import pytest
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("api/user.feature")


@given(parsers.parse('我有有效的用户数据 "{name}"'), target_fixture="user_data")
def valid_user_data(name):
    return {"name": name, "email": f"{name}@test.com"}


@given("我有空的用户名", target_fixture="user_data")
def empty_user_data():
    return {"name": ""}


@given(parsers.parse('系统中已有用户 "{name}"'), target_fixture="user_data")
def existing_user(name, api_client, base_url):
    api_client.post(f"{base_url}/api/users", json={"name": name})
    return {"name": name}


@when("我调用创建用户接口", target_fixture="api_response")
def create_user(api_client, base_url, user_data):
    resp = api_client.post(f"{base_url}/api/users", json=user_data)
    return resp


@when("我调用获取用户列表接口", target_fixture="api_response")
def list_users(api_client, base_url):
    resp = api_client.get(f"{base_url}/api/users")
    return resp


@then(parsers.parse("返回状态码 {status_code:d}"))
def check_status(api_response, status_code):
    assert api_response.status_code == status_code


@then(parsers.parse('返回的用户名称为 "{name}"'))
def check_user_name(api_response, name):
    assert api_response.json()["name"] == name


@then(parsers.parse("返回的列表长度为 {length:d}"))
def check_list_length(api_response, length):
    assert len(api_response.json()) == length
