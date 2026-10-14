# Dashboard Load Time Measurement

## Measurement context

-Date: 14/10/2026
-Database: PostgreSQL 18, 10,000 BP readings across 1,000    patients
  (seeded with `python manage.py seed_patients --count 1000 --readings 10 --seed 42`)
-Commit: 3b4a7819016a407ae098ce4430f1c8bf96afd29a
-Page measured: Clinician Dashboard (`/dashboard`) after login
-User: clinician1
-Build: Vite dev server (`npm run dev`)
-Browser: Chrome
-Network: localhost
-Cache: disabled

## Method

Chrome DevTools Network panel, "Disable cache" enabled, hard reload.
Measured time from navigation start to load event, read from the Finish
time at the bottom of the Network panel.

## Results

| Run | Finish time (s) |
|-----|-----------------|
| 1   |       1.42          |
| 2   |       1.73          |
| 3   |       1.66          |
| Median |     1.60         |
