# Load Test Notes

## Test setup

- Database: 10,000 BP readings across 1,000 patients
  (`seed_patients --count 1000 --readings 10 --seed 42`)
- Server: Waitress, 32 threads, 127.0.0.1:8000, `LOAD_TEST=1`
- Client: Locust 2.32.10 on the same Windows desktop
- Load profile: `/api/bp_readings/` (weight 3), `/api/patients/` (weight 2),
  `/api/alerts/` (weight 1), plus one `/api/auth/login/` per simulated user
- Run duration: 60 seconds per concurrency level

## Threat to validity

`LOAD_TEST=1` intentionally swaps Django to MD5 password hashing and
disables throttling. The benchmark therefore measures the application
under a controlled load profile, not a production-equivalent deployment.

The load generator, application server, and PostgreSQL all ran on the
same physical machine, competing for the same CPU cores. Absolute figures
should be read as a lower bound on production throughput.

## Results

| Users | Requests | Failures | Aggregate 95th | Aggregate 100th |
|-------|----------|----------|----------------|-----------------|
| 10    | 287      | 0 (0.00%)| 210 ms         | 300 ms          |
| 25    | 690      | 0 (0.00%)| 700 ms         | 1,600 ms        |
| 50    | 766      | 0 (0.00%)| 3,300 ms       | 3,600 ms        |

### Per-endpoint 95th percentile (50 users)

| Endpoint                | 95th     |
|-------------------------|----------|
| `/api/auth/login/`      | 520 ms   |
| `/api/alerts/`          | 2,500 ms |
| `/api/bp_readings/`     | 3,400 ms |
| `/api/patients/`        | 3,400 ms |

## Interpretation

- The system meets the 2-second 95th-percentile criterion at 10 and 25
  concurrent users.
- At 50 concurrent users the aggregate 95th percentile reaches 3,300 ms,
  exceeding the criterion. Throughput plateaus between 25 and 50 users
  (11.6 -> 12.8 req/s), indicating the shared test hardware is saturated.
- Failure rate is 0.00% at all concurrency levels, so the error-rate
  criterion (<5%) is met throughout.
- The bottleneck is shared CPU contention and query cost against a
  10,000-row dataset. Both `/api/bp_readings/` and `/api/patients/`
  involve joins and pagination over the full table; dedicated deployment
  hardware and further index work are the most likely improvements.

## Commands

Server:

```bash
export LOAD_TEST=1
waitress-serve --listen=127.0.0.1:8000 --threads=32 \
    hypertension_monitoring_and_alert_system.wsgi:application
