# tests/protocol/test_order.py
import pytest

pytestmark = pytest.mark.protocol


def test_heartbeat(step_client):
    """测试心跳"""
    resp = step_client.heartbeat()
    assert resp["type"] == "heartbeat_ack"
    assert resp["status"] == "ok"


def test_new_order(step_client):
    """测试报单"""
    resp = step_client.new_order("600000", "buy", 10.5, 100)
    assert resp["type"] == "new_order_ack"
    assert resp["status"] == "filled"
    assert resp["order_id"] > 0


def test_query_order(step_client):
    """测试查询订单"""
    resp = step_client.new_order("600001", "sell", 20.0, 200)
    order_id = resp["order_id"]
    resp = step_client.query_order(order_id)
    assert resp["type"] == "query_order_ack"
    assert resp["order"]["symbol"] == "600001"
    assert resp["order"]["status"] == "filled"


def test_cancel_order(step_client):
    """测试撤单"""
    resp = step_client.new_order("600002", "buy", 15.0, 300)
    order_id = resp["order_id"]
    resp = step_client.cancel_order(order_id)
    assert resp["type"] == "cancel_order_ack"
    assert resp["status"] == "cancelled"
    resp = step_client.query_order(order_id)
    assert resp["order"]["status"] == "cancelled"


def test_cancel_nonexistent_order(step_client):
    """测试撤销不存在的订单"""
    resp = step_client.cancel_order(99999)
    assert resp["type"] == "cancel_order_reject"


def test_query_nonexistent_order(step_client):
    """测试查询不存在的订单"""
    resp = step_client.query_order(99999)
    assert resp["type"] == "query_order_reject"
