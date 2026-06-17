"""可靠地启动并等待本地服务，替代 sleep。"""
import socket
import subprocess
import sys
import time

from common.paths import PROJECT_ROOT


def wait_for_port(host, port, timeout=10.0, interval=0.2):
    """轮询目标端口，能建立 TCP 连接即返回；超时抛 TimeoutError。

    比 sleep 更快（端口一开就返回）也更可靠（慢机器能等到开）。
    """
    deadline = time.monotonic() + timeout
    last_err = None
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=interval):
                return
        except OSError as e:
            last_err = e
            time.sleep(interval)
    raise TimeoutError(
        f"等待 {host}:{port} 在 {timeout}s 内未就绪: {last_err}"
    )


def start_service(module, host, port, cwd=PROJECT_ROOT, timeout=10.0, interval=0.2):
    """启动一个 Python 模块作为服务并等待其端口就绪。

    Args:
        module: 可被 `python -m <module>` 执行的模块点路径，
                如 "mock_services.api_mock"
        host/port: 用于就绪探测的地址端口
        cwd: 进程工作目录，默认项目根
        timeout: 端口就绪等待总时长
        interval: 轮询间隔

    Returns:
        subprocess.Popen 进程对象。失败（端口超时或进程提前退出）时
        kill 进程并抛 RuntimeError，错误信息包含捕获的 stderr。
    """
    proc = subprocess.Popen(
        [sys.executable, "-m", module],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        wait_for_port(host, port, timeout=timeout, interval=interval)
    except TimeoutError:
        proc.terminate()
        try:
            _out, err = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            err = "<进程未响应 terminate，已 kill>"
        raise RuntimeError(
            f"服务 {module} 未在 {timeout}s 内就绪于 {host}:{port}。\n"
            f"stderr:\n{err}"
        )
    finally:
        # 若进程已提前退出（如模块名错误），communicate 拿到 stderr
        if proc.poll() is not None:
            try:
                _out, err = proc.communicate(timeout=1)
            except subprocess.TimeoutExpired:
                err = "<无 stderr>"
            raise RuntimeError(
                f"服务 {module} 启动后立即退出（exit={proc.returncode}）。\n"
                f"stderr:\n{err}"
            )

    return proc
