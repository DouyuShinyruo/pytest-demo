# tests/protocol/conftest.py
import pytest
import socket
import subprocess
import time
import json


class STEPClient:
    """STEP 协议客户端"""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def close(self):
        if self.sock:
            self.sock.close()

    def send(self, msg):
        self.sock.sendall(json.dumps(msg).encode("utf-8") + b"|END")
        data = self.sock.recv(4096).decode("utf-8")
        response_str = data.replace("|END", "")
        return json.loads(response_str)

    def new_order(self, symbol, side, price, quantity):
        return self.send({
            "type": "new_order",
            "symbol": symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
        })

    def cancel_order(self, order_id):
        return self.send({"type": "cancel_order", "order_id": order_id})

    def query_order(self, order_id):
        return self.send({"type": "query_order", "order_id": order_id})

    def heartbeat(self):
        return self.send({"type": "heartbeat"})


@pytest.fixture(scope="session")
def step_server():
    """启动 STEP 模拟网关"""
    proc = subprocess.Popen(
        ["python", "mock_services/step_gateway_mock.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)
    yield proc
    proc.terminate()
    proc.wait()


@pytest.fixture(scope="function")
def step_client(config, step_server):
    """STEP 客户端"""
    host = config.get("protocol.host")
    port = config.get("protocol.port")
    client = STEPClient(host, port)
    client.connect()
    yield client
    client.close()
