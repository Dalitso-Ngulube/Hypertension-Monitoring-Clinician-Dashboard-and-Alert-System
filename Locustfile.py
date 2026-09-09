from locust import HttpUser, task, between

class HypertensionUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and store the token
        response = self.client.post("/api/auth/login/", json={
            "username": "clinician1",
            "password": "DemoPass123!"
        })
        if response.status_code == 200:
            token = response.json().get("access")
            if token:
                # Store the token in the user's session
                self.token = token
                # Set the Authorization header for all future requests
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