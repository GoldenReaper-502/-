# HAZM TUWAIQ

## Requirements
Install backend dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run Backend

```bash
python -m uvicorn backend.main:app --reload --port 8000
```

## Run Frontend

```bash
python -m http.server 4173
```

Open:
- Frontend: `http://127.0.0.1:4173/index.html`
- API Docs: `http://127.0.0.1:8000/api/docs`

## CORS
Backend CORS allows:
- `http://127.0.0.1:4173`
- `http://localhost:4173`

## Connectivity test (PowerShell)

```powershell
irm http://127.0.0.1:8000/api/platform/info
```
