# HAZM TUWAIQ — AI Safety Platform

Production-ready FastAPI + static SPA foundation for safety operations with Multi-Tenant isolation, RBAC, incidents, permits, risk, reports, and camera integration readiness.

## Project Structure

```text
.
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── errors.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── behavior.py
│   │   ├── checklists.py
│   │   ├── permits.py
│   │   └── predictive.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── assistant.py
│   │   ├── auth.py
│   │   ├── cameras.py
│   │   ├── checklists.py
│   │   ├── companies.py
│   │   ├── core_compat.py
│   │   ├── dashboard.py
│   │   ├── dev.py
│   │   ├── incidents.py
│   │   ├── permits.py
│   │   ├── platform.py
│   │   ├── reports.py
│   │   ├── risk.py
│   │   └── system.py
│   ├── services/
│   │   └── __init__.py
│   └── storage/
│       ├── __init__.py
│       ├── data.json
│       └── repository.py
├── frontend/
│   └── app.js
├── index.html
├── style.css
└── requirements.txt
```

## Install

> Run from **project root**.

```bash
python -m pip install -r requirements.txt
```

## Run Backend

> Run from **project root only** to avoid `ModuleNotFoundError: No module named 'backend'`.

```bash
python -m uvicorn backend.main:app --reload --port 8000 --app-dir .
```

Alternative stable run:

```bash
python -m backend.main
```

## Run Frontend

> Run from **project root** because `index.html` and `style.css` are in root.

```bash
python -m http.server 4173
```

Open:
- Frontend: `http://127.0.0.1:4173/index.html`
- Swagger: `http://127.0.0.1:8000/api/docs`

## RBAC Roles

- SuperAdmin
- CompanyAdmin
- SafetyManager
- Supervisor
- Inspector
- Operator
- Viewer

Default seeded credentials (demo):
- `superadmin / admin123`
- `companyadmin / admin123`
- `safety / admin123`
- `operator / admin123`
- `viewer / admin123`

## Multi-Tenant Design

- Data includes `company_id` (tenant id) where applicable.
- SuperAdmin can access all tenants.
- Other roles are tenant-scoped by `company_id`.
- Tenant isolation enforced in router operations via dependencies.

## Key Endpoints

- Health / Platform
  - `GET /health`
  - `GET /api/platform/info`
  - `GET /api/core/system/status`
- Auth / RBAC
  - `POST /api/auth/login`
  - `POST /api/auth/refresh`
  - `GET /api/auth/me`
  - `GET /api/roles`
  - `GET /api/permissions`
  - `GET /api/users`
- Multi-Tenant Entities
  - `GET /api/companies`
  - `GET /api/sites`
  - `GET /api/departments`
- Cameras
  - `GET /api/cameras`
  - `POST /api/cameras`
  - `GET /api/cameras/{id}`
  - `POST /api/cameras/{id}/test`
- Incidents / Alerts
  - `GET /api/incidents`
  - `POST /api/incidents`
  - `POST /api/incidents/{id}/assign`
  - `POST /api/incidents/{id}/notes`
  - `POST /api/incidents/{id}/close`
  - `GET /api/alerts`
- Risk
  - `POST /api/core/predict-risk`
  - `GET /api/risk-assessments`
  - `POST /api/risk-assessments`
  - `GET /api/risk-assessments/export.csv`
- Work Permits
  - `GET /api/core/work-permits`
  - `POST /api/core/work-permits`
  - `PUT /api/core/work-permits/{id}`
  - `DELETE /api/core/work-permits/{id}`
- Checklists / Inspections
  - `GET /api/core/checklists`
  - `POST /api/core/checklists`
  - `GET /api/inspections`
  - `POST /api/inspections`
- Reports
  - `GET /api/reports/incidents.csv`
  - `GET /api/reports/permits.csv`
  - `GET /api/reports/risk.csv`
- Assistant / Dev
  - `POST /api/assistant/query`
  - `POST /api/dev/seed`
  - `POST /api/dev/reset`

## Camera Integration Readiness

Current implementation is integration-ready with mock testing and adapter placeholders:
- RTSP/ONVIF discovery: TODO adapter layer
- WebRTC/HLS proxy: TODO adapter layer

This keeps current demo stable while preserving a clean extension path for real camera infrastructure.

## Smoke Tests

### 1) Python compile sanity

```bash
python -m py_compile backend/main.py backend/core/config.py backend/core/errors.py backend/core/deps.py backend/core/security.py backend/storage/repository.py
```

### 2) Package marker checks

```bash
python - <<'PY'
import os
paths = [
    'backend/__init__.py',
    'backend/core/__init__.py',
    'backend/models/__init__.py',
    'backend/routers/__init__.py',
    'backend/services/__init__.py',
    'backend/storage/__init__.py',
]
print('missing:', [p for p in paths if not os.path.exists(p)])
PY
```

### 3) Static asset checks

```bash
python -m http.server 4173
# verify /index.html, /style.css, /frontend/app.js return 200
```

## Connectivity Tests

PowerShell:

```powershell
irm http://127.0.0.1:8000/api/platform/info
irm http://127.0.0.1:8000/api/core/system/status
```

## CORS Policy

Allowed origins are configured in `backend/core/config.py` and applied in `backend/main.py`:
- `http://127.0.0.1:4173`
- `http://localhost:4173`

## Why `ModuleNotFoundError: No module named 'backend'` happens

It occurs when backend is launched from a directory other than project root, so Python cannot resolve `backend` package imports. Use root execution and `--app-dir .` as documented above.
