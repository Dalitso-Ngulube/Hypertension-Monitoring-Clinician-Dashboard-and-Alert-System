# 50-user Locust load test

## Fixed run

- Date: 15 September 2026
- Locust: 2.32.10
- Server: Waitress, 16 threads
- Target: `http://127.0.0.1:8000`
- Users: 50
- Spawn rate: 10 users/second
- Duration: 60 seconds
- Application configuration: `LOAD_TEST=1`
- Performance fixes: API page size reduced from 500 to 100; alert querysets use `select_related('patient')`
- Requests: 1,403
- Failures: 0
- Error rate: 0.00%
- Aggregate median: 40 ms
- Aggregate 95th percentile: 410 ms
- Pass criterion: 95th percentile <= 2,000 ms and error rate < 5%
- Status: **PASS**

Commands:

```bash
LOAD_TEST=1 LOCUST_USERNAME=clinician1 LOCUST_PASSWORD='DemoPass123!' waitress-serve --port=8000 --threads=16 hypertension_monitoring_and_alert_system.wsgi:application
LOCUST_USERNAME=clinician1 LOCUST_PASSWORD='DemoPass123!' locust --headless --users 50 --spawn-rate 10 --host http://127.0.0.1:8000 --run-time 60s --csv=evaluation_artifacts/load_test_50u_fixed
```

The fixed-run raw CSV files, console output, exceptions CSV, and HTML report use the `load_test_50u_fixed` prefix. The earlier `load_test_50u` run is retained as a before-fix comparison and failed the latency criterion.
