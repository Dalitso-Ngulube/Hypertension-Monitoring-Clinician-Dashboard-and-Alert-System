# Locust smoke run

- Date: 2026-09-15
- Locust: 2.32.10
- Target: `http://127.0.0.1:8001`
- Users: 2
- Spawn rate: 2 users/second
- Duration: 10 seconds
- Command: `locust -f Locustfile.py --headless --host http://127.0.0.1:8001 --users 2 --spawn-rate 2 --run-time 10s --csv logs/locust_smoke --html logs/locust_smoke.html --only-summary`
- Authentication: environment variables `LOCUST_USERNAME` and `LOCUST_PASSWORD`
- CSV result: 11 recorded requests, 0 failures
- CSV aggregate 95th percentile: 1900 ms

The console summary reported 12 requests while the generated CSV recorded 11. The CSV is preserved as the authoritative raw result. This is a smoke test, not evidence for the previously claimed 50-user scalability result.
