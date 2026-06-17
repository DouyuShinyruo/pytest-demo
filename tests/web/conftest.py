# tests/web/conftest.py
import pytest
from playwright.sync_api import sync_playwright

from common.process_utils import start_service


@pytest.fixture(scope="session")
def web_server():
    """启动 Web Mock 服务"""
    proc = start_service(
        "mock_services.web_mock",
        "127.0.0.1",
        8080,
    )
    yield proc
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="function")
def browser():
    """Playwright 浏览器实例"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def page(browser, web_server):
    """浏览器页面，每个测试一个新页面"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def base_url(config):
    """Web 服务 base_url"""
    return config.get("web.base_url")
