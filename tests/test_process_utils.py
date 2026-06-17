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


def _grab_free_port(host="127.0.0.1"):
    """bind-then-close 技巧：让系统分配一个当前空闲的端口。"""
    tmp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tmp.bind((host, 0))
    port = tmp.getsockname()[1]
    tmp.close()
    return port


def test_start_service_timeout_message_for_hanging_service():
    """服务启动但未在探测端口就绪时，错误信息应为超时提示而非「退出」。

    回归测试：修复 start_service 此前因 finally 块覆盖异常导致超时路径
    抛出误导性「立即退出」消息的问题。

    防泄漏设计：dummy 监听 socket 表示「服务确实在别处起来了」，同时探测
    另一个空闲端口（无人监听）→ wait_for_port 必然超时。start_service 在
    超时路径上内部已 terminate 该进程，且 C1 已令 api_mock 为单进程
    （use_reloader=False），故终止即彻底回收，不残留 reloader 子进程。
    finally 确保 dummy 监听 socket 被关闭。
    """
    p_listen = _grab_free_port()
    p_probe = _grab_free_port()
    stop = _start_listener("127.0.0.1", p_listen)
    try:
        # p_listen 上有 dummy 监听（表示服务已起），但探测 p_probe（空闲）
        with pytest.raises(RuntimeError) as exc_info:
            start_service(
                "mock_services.api_mock", "127.0.0.1", p_probe, timeout=3.0
            )
        msg = str(exc_info.value)
        assert "未在" in msg and "就绪" in msg   # 超时提示
        assert "立即退出" not in msg              # 不能是误导性的「退出」消息
    finally:
        # 回收 dummy 监听 socket，杜绝本测试自身的资源占用。
        stop()
