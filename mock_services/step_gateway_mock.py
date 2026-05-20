# mock_services/step_gateway_mock.py
import socket
import threading
import json
import time


class STEPGateway:
    """模拟 STEP 交易网关"""

    def __init__(self, host="localhost", port=9000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.orders = {}
        self.next_order_id = 1
        self.running = False

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        print(f"STEP 网关启动: {self.host}:{self.port}")

        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client, addr = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client, args=(client,), daemon=True
                ).start()
            except socket.timeout:
                continue

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()

    def _handle_client(self, client):
        buffer = ""
        try:
            while self.running:
                data = client.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")

                while "|END" in buffer:
                    msg_str, buffer = buffer.split("|END", 1)
                    response = self._process_message(msg_str.strip())
                    client.sendall((json.dumps(response) + "|END").encode("utf-8"))
        except Exception as e:
            print(f"客户端处理异常: {e}")
        finally:
            client.close()

    def _process_message(self, msg_str):
        try:
            msg = json.loads(msg_str)
        except json.JSONDecodeError:
            return {"type": "error", "msg": "无效的 JSON 消息"}

        msg_type = msg.get("type")

        if msg_type == "new_order":
            return self._new_order(msg)
        elif msg_type == "cancel_order":
            return self._cancel_order(msg)
        elif msg_type == "query_order":
            return self._query_order(msg)
        elif msg_type == "heartbeat":
            return {"type": "heartbeat_ack", "status": "ok"}
        else:
            return {"type": "error", "msg": f"未知消息类型: {msg_type}"}

    def _new_order(self, msg):
        order_id = self.next_order_id
        self.next_order_id += 1

        order = {
            "order_id": order_id,
            "symbol": msg.get("symbol", ""),
            "side": msg.get("side", "buy"),
            "price": msg.get("price", 0),
            "quantity": msg.get("quantity", 0),
            "status": "filled",
        }
        self.orders[order_id] = order

        return {
            "type": "new_order_ack",
            "order_id": order_id,
            "status": "filled",
        }

    def _cancel_order(self, msg):
        order_id = msg.get("order_id")
        if order_id not in self.orders:
            return {"type": "cancel_order_reject", "order_id": order_id, "msg": "订单不存在"}

        order = self.orders[order_id]
        if order["status"] == "cancelled":
            return {"type": "cancel_order_reject", "order_id": order_id, "msg": "订单已撤销"}

        order["status"] = "cancelled"
        return {"type": "cancel_order_ack", "order_id": order_id, "status": "cancelled"}

    def _query_order(self, msg):
        order_id = msg.get("order_id")
        if order_id not in self.orders:
            return {"type": "query_order_reject", "order_id": order_id, "msg": "订单不存在"}

        return {"type": "query_order_ack", "order": self.orders[order_id]}


def run_gateway(host="localhost", port=9000):
    gateway = STEPGateway(host, port)
    gateway.start()
    return gateway


if __name__ == "__main__":
    run_gateway()
