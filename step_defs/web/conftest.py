import pytest
from playwright.sync_api import sync_playwright

# web_server 复用根 conftest.py 的 session 级全局服务（端口 8080）。


@pytest.fixture(scope="function")
def browser():
    """Playwright 浏览器实例"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser, web_server):
    """浏览器页面"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def base_url(config):
    """Web 服务 base_url"""
    return config.get("web.base_url")
