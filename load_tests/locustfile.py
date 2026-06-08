from locust import HttpUser, task, between

class PalladiumUser(HttpUser):
    wait_time = between(1, 5)
    token = None

    def on_start(self):
        # Authenticate and get token
        response = self.client.post("/api/v1/auth/login", data={"username": "admin@example.com", "password": "Password123!"})
        if response.status_code == 200:
            self.token = response.json().get("access_token")

    @task(3)
    def view_campaigns(self):
        if self.token:
            self.client.get("/api/v1/campaigns", headers={"Authorization": f"Bearer {self.token}"})

    @task(2)
    def view_analytics(self):
        if self.token:
            self.client.get("/api/v1/analytics/overview", headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def generate_report(self):
        if self.token:
            self.client.post("/api/v1/reports/generate", json={"type": "campaign", "format": "json"}, headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def view_health(self):
        self.client.get("/api/v1/health/")
