import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from playwright.sync_api import Page

scenarios("web/login.feature")


@given("我打开登录页面")
def open_login(page: Page, base_url):
    page.goto(f"{base_url}/login")


@when(parsers.parse('我输入用户名 "{username}" 和密码 "{password}"'))
def fill_credentials(page: Page, username, password):
    page.fill("#username", username)
    page.fill("#password", password)


@when("我点击登录按钮")
def click_login(page: Page):
    page.click("#login-btn")


@then("我应该跳转到控制台页面")
def check_dashboard(page: Page):
    page.wait_for_url("**/dashboard")


@then(parsers.parse('页面显示 "{text}"'))
def check_page_text(page: Page, text):
    content = page.content()
    assert text in content


@then(parsers.parse('我应该看到错误提示 "{message}"'))
def check_error_message(page: Page, message):
    assert page.locator("#error-msg").is_visible()
    assert message in page.locator("#error-msg").inner_text()
