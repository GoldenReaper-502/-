# HAZM TUWAIQ — AI Safety Platform

## Project structure

```text
.
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── storage/
│   └── modules/
├── frontend/
│   └── app.js
├── index.html
├── style.css
└── requirements.txt
```

## Why `ModuleNotFoundError: No module named 'backend'` happens

`backend` is a Python package. If you run uvicorn from outside project root, that package is not on `PYTHONPATH`, so imports fail.

## Install

```bash
python -m pip install -r requirements.txt
```

## Run (from project root)

### Backend

```bash
python -m uvicorn backend.main:app --reload --port 8000 --app-dir .
```

Alternative:

```bash
python -m backend.main
```

### Frontend (static)

```bash
python -m http.server 4173
```

Open:
- Frontend: `http://127.0.0.1:4173/index.html`
- API Docs: `http://127.0.0.1:8000/api/docs`

## CORS

Allowed origins:
- `http://127.0.0.1:4173`
- `http://localhost:4173`

## Seed / Reset

```bash
curl -X POST http://127.0.0.1:8000/api/dev/reset
curl -X POST http://127.0.0.1:8000/api/dev/seed
```

## Auth quick login

Default demo users:
- `superadmin / admin123`
- `companyadmin / admin123`
- `safety / admin123`
- `operator / admin123`
- `viewer / admin123`

## Smoke tests

### Compile checks

```bash
python -m py_compile backend/main.py backend/core/config.py backend/core/errors.py backend/core/security.py backend/core/deps.py
```

### `__init__.py` marker checks

```bash
python - <<'PY'
import os
paths = [
    'backend/__init__.py','backend/core/__init__.py','backend/routers/__init__.py','backend/models/__init__.py',
    'backend/storage/__init__.py','backend/services/__init__.py','backend/modules/__init__.py',
    'backend/modules/core/__init__.py','backend/modules/risk/__init__.py','backend/modules/behavior/__init__.py',
    'backend/modules/checklists/__init__.py','backend/modules/work_permits/__init__.py','backend/modules/dashboard/__init__.py',
]
print('missing:', [p for p in paths if not os.path.exists(p)])
PY
```

### PowerShell connectivity

```powershell
irm http://127.0.0.1:8000/api/platform/info
```

## Key endpoints

- `/health`
- `/api/platform/info`
- `/api/core/system/status`
- `/api/auth/login`
- `/api/dashboard`
- `/api/cameras` + `/api/cameras/{id}/test`
- `/api/incidents` + assign/notes/close
- `/api/core/predict-risk`
- `/api/core/work-permits`
- `/api/core/checklists`
- `/api/inspections`
- `/api/reports/*.csv`
- `/api/assistant/query`

## Notes

- Camera integration adapters (RTSP/ONVIF discovery, WebRTC/HLS proxy) are scaffolded as TODO placeholders in API responses.
- Reports support CSV now; PDF is TODO.
