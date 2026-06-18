"""可靠地启动并等待本地服务，替代 sleep。"""
import socket
import subprocess
import sys
import threading
import time

from common.paths import PROJECT_ROOT

# 管道缓冲区大约 64KB；长生命周期服务（如被 locust 高频调用）会持续写日志，
# 一旦缓冲区写满又无人读取，进程会阻塞在写操作上，导致服务假死、后续请求挂起。
# 排空线程持续读走输出，仅保留末尾用于失败诊断。
_LOG_TAIL_BYTES = 16 * 1024


class _PipeTail:
    """持续累积管道输出并仅保留末尾，兼顾「不阻塞写入」与「失败可诊断」。"""

    def __init__(self, max_bytes=_LOG_TAIL_BYTES):
        self._chunks = []
        self._size = 0
        self._max = max_bytes
        self._lock = threading.Lock()

    def append(self, text):
        with self._lock:
            self._chunks.append(text)
            self._size += len(text)
            # 超容量时从头部丢弃，保留最近的内容
            while self._size > self._max and len(self._chunks) > 1:
                self._size -= len(self._chunks.pop(0))

    def text(self):
        with self._lock:
            return "".join(self._chunks)


def _drain_pipe(stream, tail):
    """后台读取一根管道写入 tail，直到流关闭（EOF）。"""
    try:
        for line in stream:
            tail.append(line)
    except (ValueError, OSError):
        # 流已被关闭/进程已退出
        pass


def wait_for_port(host, port, proc=None, timeout=10.0, interval=0.2):
    """轮询目标端口，能建立 TCP 连接即返回；超时抛 TimeoutError。

    若提供 ``proc``，则在轮询期间持续监控子进程存活：子进程一旦提前退出
    （例如模块导入失败、端口被占用导致 bind 失败）立即抛 RuntimeError，
    不必傻等端口超时——也避免「端口开着但属于别的进程」造成的误判。

    比 sleep 更快（端口一开就返回）也更可靠（慢机器能等到开）。
    """
    deadline = time.monotonic() + timeout
    last_err = None
    while time.monotonic() < deadline:
        if proc is not None and proc.poll() is not None:
            raise RuntimeError(
                f"服务进程在端口 {host}:{port} 就绪前已退出"
                f"（exit={proc.returncode}），可能端口被占用或模块启动失败。"
            )
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
        subprocess.Popen 进程对象。失败（端口超时或子进程提前退出）时
        清理进程并抛 RuntimeError，错误信息包含捕获的输出末尾。

    注意：子进程的 stdout/stderr 由后台线程持续排空（仅留末尾），故服务可
    长时间运行而不因管道缓冲区写满阻塞。
    """
    proc = subprocess.Popen(
        [sys.executable, "-m", module],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    tail = _PipeTail()
    drainers = [
        threading.Thread(target=_drain_pipe, args=(proc.stdout, tail), daemon=True),
        threading.Thread(target=_drain_pipe, args=(proc.stderr, tail), daemon=True),
    ]
    for t in drainers:
        t.start()

    def _cleanup():
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        # 等排空线程读完管道末尾，确保诊断信息完整
        for t in drainers:
            t.join(timeout=1)

    try:
        wait_for_port(host, port, proc=proc, timeout=timeout, interval=interval)
    except TimeoutError:
        _cleanup()
        raise RuntimeError(
            f"服务 {module} 未在 {timeout}s 内就绪于 {host}:{port}。"
            f"（进程仍在运行但未监听探测端口，请确认端口配置）\n"
            f"输出末尾:\n{tail.text()}"
        )
    except RuntimeError:
        _cleanup()
        raise RuntimeError(
            f"服务 {module} 启动后立即退出。\n输出末尾:\n{tail.text()}"
        )

    return proc
