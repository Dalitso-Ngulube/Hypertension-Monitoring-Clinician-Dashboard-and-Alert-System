# Dashboard Load Time Measurement

Date:10/11/2026
Browser: Chrome
Network: localhost
Cache: disabled

## Method

Chrome DevTools Network panel, "Disable cache" enabled, hard reload.
Measured time from navigation start to load event, read from the Finish
time at the bottom of the Network panel.

## Results

| Run | Finish time (s) |
|-----|-----------------|
| 1   |       1.42          |
| 2   |       1.72          |
| 3   |       1.66          |
| Median |     1.60         |
