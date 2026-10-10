# Security Checks

Date: 2026-10-09  
Environment: Local Django development server (`DEBUG=True`), PostgreSQL 18.4, database `hypertension_db`. This is not the requested Waitress/`DEBUG=False` production-like configuration.  
Commit: `269d0492e902afb399e1b40f6759ffdec2b38fa7` (HEAD before these uncommitted fixes)

Checks were sent to the local server at `http://localhost:8000`. A disposable
patient user was created for the role/injection probes; access/refresh tokens
and password values are intentionally omitted from this evidence.

## Check 1 — Unauthenticated refusal

Command: `curl.exe -i --max-time 5 http://localhost:8000/api/patients/`  
Result: HTTP 403 Forbidden (DRF refusal; expected 401 or 403).  
Evidence:

```text
HTTP/1.1 403 Forbidden
Date: Fri, 09 Oct 2026 19:28:04 GMT
Server: WSGIServer/0.2 CPython/3.12.8
Content-Type: application/json
Allow: GET, POST, HEAD, OPTIONS
X-Frame-Options: DENY
Content-Length: 58

{"detail":"Authentication credentials were not provided."}
```

## Check 2 — Cross-role request refused

Command: Patient JWT `POST /api/patients/` with a harmless patient payload.  
Result: HTTP 403 Forbidden.  
Evidence:

```text
HTTP 403 Forbidden
{"detail":"Patients are not allowed to create patient records."}
```

## Check 3 — Injection probe

Probe A: `GET /api/patients/?search=%27+OR+%271%27%3D%271` with the disposable
patient token. Result: HTTP 200; only that authenticated patient's one row
was returned; no additional records were exposed.

```text
HTTP 200 OK
{"count":1,"next":null,"previous":null,"results":[{"id":661,"first_name":"","last_name":"","age":0,"gender":"","phone_number":"+15550001234","address":"","created_at":"2026-10-09T19:29:58.496929Z","updated_at":"2026-10-09T19:29:58.496929Z","user":7,"clinician":null}]}
```

Probe B: `POST /api/auth/login/` with SQL-like username `' OR 1=1 --` and a
non-real password. Result: HTTP 401; no login or data disclosure.

```text
HTTP 401 Unauthorized
{"detail":"No active account found with the given credentials"}
```

Read-only source scan for `.raw(`, `RawSQL`, `cursor()`, and `execute(` across
application Python packages returned no matches. The inspected endpoint uses
Django ORM filters; this source scan is supporting evidence, not a formal
database-query audit.

## Check 4 — Event logging

Action: Three invalid-password attempts against the disposable test account.  
Result: Three HTTP 401 responses. `logs/security.log` recorded each username,
client IP, reason, and timestamp. No password or token was logged.

Evidence (three attempt entries):

```text
WARNING 2026-10-09 21:30:12,367 monitoring 29192 27944 [SECURITY] Failed login: username=security_probe_20261009192953216570 ip=127.0.0.1 reason=Invalid credentials
WARNING 2026-10-09 21:30:15,589 monitoring 29192 21644 [SECURITY] Failed login: username=security_probe_20261009192953216570 ip=127.0.0.1 reason=Invalid credentials
WARNING 2026-10-09 21:30:18,683 monitoring 29192 17504 [SECURITY] Failed login: username=security_probe_20261009192953216570 ip=127.0.0.1 reason=Invalid credentials
```

Unauthenticated and invalid-token requests also produced `Unauthorized
request` entries. These checks were performed against the local development
server; repeat them with Waitress and `DEBUG=False` before claiming production
environment verification.
