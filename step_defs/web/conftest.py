import pytest
import subprocess
import time
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def web_server():
    """启动 Web Mock 服务"""
    proc = subprocess.Popen(
        ["python", "mock_services/web_mock.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
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
    """浏览器页面"""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def base_url(config):
    """Web 服务 base_url"""
    return config.get("web.base_url")
