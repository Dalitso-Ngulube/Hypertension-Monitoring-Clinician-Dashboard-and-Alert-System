import os

from locust import HttpUser, task, between

class HypertensionUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        username = os.environ.get("LOCUST_USERNAME")
        password = os.environ.get("LOCUST_PASSWORD")
        if not username or not password:
            raise RuntimeError("LOCUST_USERNAME and LOCUST_PASSWORD must be set")

        response = self.client.post("/api/auth/login/", json={
            "username": username,
            "password": password,
        })
        if response.status_code == 200:
            token = response.json().get("access")
            if token:
                self.token = token
                self.client.headers.update({
                    "Authorization": f"Bearer {token}"
                })
        else:
            print("Login failed:", response.text)

    @task(3)
    def view_readings(self):
        self.client.get("/api/bp_readings/")

    @task(2)
    def view_patients(self):
        self.client.get("/api/patients/")

    @task(1)
    def view_alerts(self):
        self.client.get("/api/alerts/")