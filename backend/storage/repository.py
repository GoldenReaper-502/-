from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

DB_FILE = Path(__file__).resolve().parent / 'data.json'


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Repository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._data: dict = {}
        self.load()

    def _empty(self) -> dict:
        return {
            'companies': [],
            'sites': [],
            'departments': [],
            'permissions': [],
            'roles': [],
            'users': [],
            'cameras': [],
            'incidents': [],
            'alerts': [],
            'risk_assessments': [],
            'permits': [],
            'checklists': [],
            'inspections': [],
            'audit_logs': [],
        }

    def load(self) -> None:
        with self._lock:
            if DB_FILE.exists():
                self._data = json.loads(DB_FILE.read_text(encoding='utf-8'))
            else:
                self._data = self._empty()
                self.seed()

    def save(self) -> None:
        with self._lock:
            DB_FILE.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding='utf-8')

    def reset(self) -> None:
        with self._lock:
            self._data = self._empty()
            self.seed()

    def seed(self) -> None:
        if self._data.get('users'):
            return
        tenant_a = str(uuid4())
        tenant_b = str(uuid4())
        site_a = str(uuid4())
        site_b = str(uuid4())

        self._data['companies'] = [
            {'id': tenant_a, 'name': 'HAZM Energy', 'created_at': now_iso()},
            {'id': tenant_b, 'name': 'TUWAIQ Industrial', 'created_at': now_iso()},
        ]
        self._data['sites'] = [
            {'id': site_a, 'company_id': tenant_a, 'name': 'Plant A'},
            {'id': site_b, 'company_id': tenant_b, 'name': 'Refinery B'},
        ]
        self._data['departments'] = [
            {'id': str(uuid4()), 'company_id': tenant_a, 'site_id': site_a, 'name': 'Safety'},
            {'id': str(uuid4()), 'company_id': tenant_a, 'site_id': site_a, 'name': 'Operations'},
        ]
        permissions = [
            'users:manage', 'roles:manage', 'incidents:manage', 'permits:approve', 'cameras:operate',
            'reports:view', 'risk:manage', 'inspections:manage', 'dashboard:view'
        ]
        self._data['permissions'] = [{'id': str(uuid4()), 'name': p} for p in permissions]
        self._data['roles'] = [
            {'id': str(uuid4()), 'name': 'SuperAdmin', 'permissions': permissions},
            {'id': str(uuid4()), 'name': 'CompanyAdmin', 'permissions': permissions[:-1] + ['dashboard:view']},
            {'id': str(uuid4()), 'name': 'SafetyManager', 'permissions': ['incidents:manage', 'risk:manage', 'reports:view', 'dashboard:view', 'inspections:manage']},
            {'id': str(uuid4()), 'name': 'Supervisor', 'permissions': ['permits:approve', 'incidents:manage', 'dashboard:view']},
            {'id': str(uuid4()), 'name': 'Inspector', 'permissions': ['inspections:manage', 'incidents:manage', 'dashboard:view']},
            {'id': str(uuid4()), 'name': 'Operator', 'permissions': ['cameras:operate', 'dashboard:view']},
            {'id': str(uuid4()), 'name': 'Viewer', 'permissions': ['dashboard:view']},
        ]
        self._data['users'] = [
            {'id': str(uuid4()), 'username': 'superadmin', 'password': 'admin123', 'role': 'SuperAdmin', 'company_id': None},
            {'id': str(uuid4()), 'username': 'companyadmin', 'password': 'admin123', 'role': 'CompanyAdmin', 'company_id': tenant_a},
            {'id': str(uuid4()), 'username': 'safety', 'password': 'admin123', 'role': 'SafetyManager', 'company_id': tenant_a},
            {'id': str(uuid4()), 'username': 'operator', 'password': 'admin123', 'role': 'Operator', 'company_id': tenant_a},
            {'id': str(uuid4()), 'username': 'viewer', 'password': 'admin123', 'role': 'Viewer', 'company_id': tenant_a},
        ]
        self._data['cameras'] = [
            {'id': str(uuid4()), 'company_id': tenant_a, 'site_id': site_a, 'name': 'Gate Cam', 'stream_url': 'rtsp://demo/gate', 'vendor': 'Hikvision', 'location': 'Main Gate', 'status': 'online'},
            {'id': str(uuid4()), 'company_id': tenant_a, 'site_id': site_a, 'name': 'Boiler Cam', 'stream_url': 'rtsp://demo/boiler', 'vendor': 'Dahua', 'location': 'Boiler', 'status': 'offline'},
        ]
        self._data['permits'] = [
            {'id': str(uuid4()), 'company_id': tenant_a, 'site_id': site_a, 'title': 'Hot Work', 'risk_level': 'High', 'approver': 'Supervisor A', 'checklist_items': ['PPE', 'Gas test'], 'status': 'approved', 'created_at': now_iso()},
            {'id': str(uuid4()), 'company_id': tenant_a, 'site_id': site_a, 'title': 'Confined Space', 'risk_level': 'Medium', 'approver': '', 'checklist_items': ['Permit board'], 'status': 'submitted', 'created_at': now_iso()},
        ]
        self._data['incidents'] = [
            {'id': str(uuid4()), 'company_id': tenant_a, 'site_id': site_a, 'camera_id': None, 'type': 'Near Miss', 'severity': 'Medium', 'status': 'Open', 'description': 'Slip near pump', 'assigned_to': None, 'notes': [], 'created_at': now_iso(), 'closed_at': None},
        ]
        self._data['alerts'] = [
            {'id': str(uuid4()), 'company_id': tenant_a, 'message': 'Helmet missing detection', 'severity': 'High', 'created_at': now_iso()},
        ]
        self._data['risk_assessments'] = [
            {'id': str(uuid4()), 'company_id': tenant_a, 'hazard': 'Working at height', 'likelihood': 4, 'severity': 4, 'risk_score': 16, 'controls': ['Harness'], 'residual_score': 8, 'level': 'High', 'created_at': now_iso()}
        ]
        self._data['checklists'] = [
            {'id': str(uuid4()), 'company_id': tenant_a, 'name': 'Excavator Daily', 'equipment_type': 'Excavator', 'camera_id': None, 'items': ['Brakes', 'Alarm'], 'created_at': now_iso(), 'updated_at': now_iso()}
        ]
        self._data['inspections'] = [
            {'id': str(uuid4()), 'company_id': tenant_a, 'template_id': None, 'score': 85, 'findings': ['Oil leak minor'], 'attachments': [], 'created_at': now_iso()}
        ]
        self._data['audit_logs'] = []
        self.save()

    def all(self, key: str) -> list[dict]:
        return deepcopy(self._data.get(key, []))

    def list_tenant(self, key: str, company_id: str | None) -> list[dict]:
        items = self._data.get(key, [])
        if company_id is None:
            return deepcopy(items)
        return deepcopy([i for i in items if i.get('company_id') == company_id])

    def get(self, key: str, item_id: str) -> dict | None:
        for item in self._data.get(key, []):
            if item.get('id') == item_id:
                return deepcopy(item)
        return None

    def create(self, key: str, payload: dict) -> dict:
        item = {'id': str(uuid4()), **payload}
        self._data[key].append(item)
        self.save()
        return deepcopy(item)

    def update(self, key: str, item_id: str, patch: dict) -> dict | None:
        for idx, item in enumerate(self._data.get(key, [])):
            if item.get('id') == item_id:
                self._data[key][idx] = {**item, **patch}
                self.save()
                return deepcopy(self._data[key][idx])
        return None

    def delete(self, key: str, item_id: str) -> bool:
        for idx, item in enumerate(self._data.get(key, [])):
            if item.get('id') == item_id:
                del self._data[key][idx]
                self.save()
                return True
        return False

    def get_user(self, user_id: str | None) -> dict | None:
        if not user_id:
            return None
        for u in self._data.get('users', []):
            if u.get('id') == user_id:
                return deepcopy(u)
        return None

    def find_user_credentials(self, username: str, password: str) -> dict | None:
        for u in self._data.get('users', []):
            if u.get('username') == username and u.get('password') == password:
                return deepcopy(u)
        return None

    def append_audit(self, action: str, user_id: str | None, company_id: str | None, details: dict | None = None) -> None:
        self._data['audit_logs'].append(
            {
                'id': str(uuid4()),
                'action': action,
                'user_id': user_id,
                'company_id': company_id,
                'details': details or {},
                'created_at': now_iso(),
            }
        )
        self.save()


repo = Repository()
