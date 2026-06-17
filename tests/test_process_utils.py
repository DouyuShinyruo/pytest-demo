import socket
import threading
import pytest
from common.process_utils import wait_for_port, start_service


def _start_listener(host, port):
    """在子线程开一个监听 socket，返回一个 stop() 函数"""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(1)
    srv.settimeout(0.2)

    def _accept_loop():
        while not srv._closed:
            try:
                conn, _ = srv.accept()
                conn.close()
            except socket.timeout:
                continue
            except OSError:
                break

    srv._closed = False
    t = threading.Thread(target=_accept_loop, daemon=True)
    t.start()

    def stop():
        srv._closed = True
        srv.close()

    return stop


def test_wait_for_port_returns_when_open():
    """端口开放时立即返回，不抛异常"""
    host, port = "127.0.0.1", 0
    # 让系统分配一个空闲端口
    tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tmp.bind((host, 0))
    port = tmp.getsockname()[1]
    tmp.close()

    stop = _start_listener(host, port)
    try:
        # 不抛异常即视为成功
        wait_for_port(host, port, timeout=3.0)
    finally:
        stop()


def test_wait_for_port_times_out_when_closed():
    """端口关闭时超时抛 TimeoutError"""
    # 选一个极不可能被占用的端口
    tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tmp.bind(("127.0.0.1", 0))
    port = tmp.getsockname()[1]
    tmp.close()  # 立即关闭，端口空闲

    with pytest.raises(TimeoutError):
        wait_for_port("127.0.0.1", port, timeout=1.0, interval=0.1)


def test_start_service_failure_includes_stderr():
    """启动一个必然失败的服务（端口冲突模拟：用一个会立即报错的模块路径不可行，
    改用端口已被占用导致 wait_for_port 超时——这里测模块名错误导致进程立即退出）"""
    # 用一个不存在的模块，进程会立即退出且 stderr 含 traceback
    with pytest.raises(RuntimeError) as exc_info:
        start_service("this.module.does.not.exist", "127.0.0.1", 0, timeout=2.0)
    # 错误信息里应包含进程产出的 stderr（No module named ...）
    assert "No module named" in str(exc_info.value)
