"""阈值回归测试专用场景：短等待时间，在 15s 内积累足够样本，
让失败率门槛具备统计意义（单次冷启动抖动不再显著影响失败率）。

手动交互式压测仍使用 locustfile.py（保留贴近真实用户的 think-time）。
"""
from locust import HttpUser, task, between


class FastAPIUser(HttpUser):
    """快速 API 用户：低等待时间，用于阈值测试的高吞吐采样"""

    wait_time = between(0.2, 0.5)

    @task(3)
    def create_user(self):
        """创建用户（权重 3）"""
        self.client.post(
            "/api/users",
            json={"name": "perf", "email": "perf@example.com"},
        )

    @task(2)
    def list_users(self):
        """获取用户列表（权重 2）"""
        self.client.get("/api/users")

    @task(1)
    def get_user(self):
        """获取单个用户（权重 1）"""
        self.client.get("/api/users/1")

    def on_start(self):
        """用户启动时重置数据"""
        self.client.post("/api/reset")
