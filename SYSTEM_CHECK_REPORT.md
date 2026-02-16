# System Check Report (HAZM TUWAIQ)

## Backend
- Modular FastAPI app available via `backend.main:create_app` and `app = create_app()`.
- Multi-tenant entities seeded: companies, sites, departments, users, roles, cameras, permits, incidents.
- CORS allows frontend origins:
  - `http://127.0.0.1:4173`
  - `http://localhost:4173`
- Core endpoints ready: platform info, system status, auth, dashboard, cameras, incidents, risk, permits, checklists, inspections, reports, assistant, dev seed/reset.

## Frontend
- Sidebar pages are implemented and routable:
  - Dashboard
  - Cameras
  - Detection
  - AI Assistant
  - Incidents
  - Risk
  - Inspections
  - Reports
  - Work Permits
  - Behavior Analysis
- Text visibility issue fixed by explicit high-contrast palette, no hidden opacity text, and stable layout rules.

## Run Commands
- Backend: `python -m uvicorn backend.main:app --reload --port 8000 --app-dir .`
- Frontend: `python -m http.server 4173`

## Smoke
- Compile and package marker checks included in README.
