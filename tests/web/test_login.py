# tests/web/test_login.py
import pytest

pytestmark = pytest.mark.web


def test_home_page(page, base_url):
    """测试首页可访问"""
    page.goto(base_url)
    assert "测试平台" in page.title()
    assert page.locator("h1").inner_text() == "欢迎来到测试平台"


def test_login_page_display(page, base_url):
    """测试登录页面显示"""
    page.goto(f"{base_url}/login")
    assert page.locator("#username").is_visible()
    assert page.locator("#password").is_visible()
    assert page.locator("#login-btn").is_visible()


def test_login_success(page, base_url):
    """测试登录成功"""
    page.goto(f"{base_url}/login")
    page.fill("#username", "admin")
    page.fill("#password", "123456")
    page.click("#login-btn")
    page.wait_for_url("**/dashboard")
    assert "admin" in page.locator("#user-info").inner_text()


def test_login_wrong_password(page, base_url):
    """测试密码错误"""
    page.goto(f"{base_url}/login")
    page.fill("#username", "admin")
    page.fill("#password", "wrong")
    page.click("#login-btn")
    assert page.locator("#error-msg").is_visible()
    assert "错误" in page.locator("#error-msg").inner_text()


def test_login_empty_fields(page, base_url):
    """测试空用户名密码"""
    page.goto(f"{base_url}/login")
    page.click("#login-btn")
    assert page.locator("#error-msg").is_visible()


def test_logout(page, base_url):
    """测试退出登录"""
    page.goto(f"{base_url}/login")
    page.fill("#username", "admin")
    page.fill("#password", "123456")
    page.click("#login-btn")
    page.wait_for_url("**/dashboard")
    page.click("#logout-btn")
    page.wait_for_url("**/login")
