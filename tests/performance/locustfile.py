from locust import HttpUser, task, between


class APIUser(HttpUser):
    """模拟 API 用户行为"""
    wait_time = between(1, 3)

    @task(3)
    def create_user(self):
        """创建用户（权重 3）"""
        self.client.post("/api/users", json={
            "name": f"user_{self.environment.runner.user_count}",
            "email": "test@example.com",
        })

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
