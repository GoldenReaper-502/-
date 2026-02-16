(() => {
  const API_BASE_URL =
    window.location.port === '4173' && ['127.0.0.1', 'localhost'].includes(window.location.hostname)
      ? 'http://127.0.0.1:8000/api'
      : '/api';

  const state = {
    token: localStorage.getItem('hazm_token') || '',
    refreshToken: localStorage.getItem('hazm_refresh') || '',
    user: JSON.parse(localStorage.getItem('hazm_user') || 'null'),
    chart: null,
    pagesByRole: {
      SuperAdmin: ['dashboard', 'cameras', 'detection', 'assistant', 'incidents', 'risk', 'inspections', 'reports', 'permits', 'behavior'],
      CompanyAdmin: ['dashboard', 'cameras', 'assistant', 'incidents', 'risk', 'inspections', 'reports', 'permits', 'behavior'],
      SafetyManager: ['dashboard', 'incidents', 'risk', 'inspections', 'reports', 'permits', 'behavior', 'assistant'],
      Supervisor: ['dashboard', 'incidents', 'permits', 'reports', 'assistant'],
      Inspector: ['dashboard', 'incidents', 'inspections', 'risk', 'assistant'],
      Operator: ['dashboard', 'cameras', 'detection', 'incidents', 'permits', 'assistant'],
      Viewer: ['dashboard', 'reports'],
    },
  };

  function headers() {
    return {
      'Content-Type': 'application/json',
      ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}),
    };
  }

  async function api(path, options = {}) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method || 'GET',
      headers: { ...headers(), ...(options.headers || {}) },
      body: options.body,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.message || data.detail || data.error || `HTTP ${res.status}`);
    return data;
  }

  function showMsg(target, content, cls = '') {
    const el = document.getElementById(target);
    if (!el) return;
    el.className = `result ${cls}`;
    el.textContent = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
  }

  function guardNav() {
    const allowed = state.pagesByRole[state.user?.role] || ['dashboard'];
    document.querySelectorAll('.nav-item').forEach((a) => {
      const page = a.dataset.page;
      a.style.display = allowed.includes(page) ? 'block' : 'none';
    });
  }

  function setAuthUI() {
    const who = document.getElementById('whoami');
    if (!who) return;
    who.textContent = state.user ? `${state.user.username} | ${state.user.role}` : 'غير مسجل';
    guardNav();
  }

  function activatePage(page) {
    document.querySelectorAll('.page').forEach((p) => p.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach((n) => n.classList.remove('active'));
    const pageEl = document.getElementById(`${page}Page`);
    const nav = document.querySelector(`.nav-item[data-page="${page}"]`);
    if (pageEl) pageEl.classList.add('active');
    if (nav) nav.classList.add('active');
    loadPage(page);
  }

  async function login() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    try {
      const data = await api('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      state.token = data.access_token;
      state.refreshToken = data.refresh_token;
      state.user = data.user;
      localStorage.setItem('hazm_token', state.token);
      localStorage.setItem('hazm_refresh', state.refreshToken);
      localStorage.setItem('hazm_user', JSON.stringify(state.user));
      setAuthUI();
      await loadDashboard();
      activatePage('dashboard');
    } catch (err) {
      alert(`Login failed: ${err.message}`);
    }
  }

  async function runSeed() {
    try {
      await api('/dev/reset', { method: 'POST' });
      alert('Seed complete. Login again if needed.');
      await loadDashboard();
    } catch (err) {
      alert(`Seed failed: ${err.message}`);
    }
  }

  async function loadDashboard() {
    const d = await api('/dashboard');
    document.getElementById('kpi-risk').textContent = d.kpis.global_risk_score;
    document.getElementById('kpi-open').textContent = d.kpis.incidents_open;
    document.getElementById('kpi-permits').textContent = d.kpis.permits_active;
    document.getElementById('kpi-alerts').textContent = d.kpis.smart_alerts;

    const ctx = document.getElementById('dashboardChart');
    if (ctx && window.Chart) {
      if (state.chart) state.chart.destroy();
      state.chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: d.charts.incidents_by_status.map((x) => x.label),
          datasets: [{ label: 'Incidents', data: d.charts.incidents_by_status.map((x) => x.value) }],
        },
        options: { responsive: true },
      });
    }
  }

  async function loadCameras() {
    const items = await api('/cameras');
    const box = document.getElementById('camera-list');
    box.innerHTML = items
      .map(
        (c) => `<div class="item-card">
        <strong>${c.name}</strong> — ${c.location}<br>
        <span class="badge ${c.status === 'online' ? 'ok' : 'fail'}">${c.status}</span>
        <button class="btn" onclick="testCamera('${c.id}')">Test</button>
        <button class="btn secondary" onclick="viewCamera('${c.id}')">View</button>
      </div>`
      )
      .join('');
  }

  async function createCamera() {
    const payload = {
      name: document.getElementById('cam-name').value,
      site_id: document.getElementById('cam-site').value,
      stream_url: document.getElementById('cam-url').value,
      vendor: document.getElementById('cam-vendor').value,
      location: document.getElementById('cam-location').value,
      status: 'online',
    };
    await api('/cameras', { method: 'POST', body: JSON.stringify(payload) });
    await loadCameras();
  }

  async function testCamera(id) {
    const res = await api(`/cameras/${id}/test`, { method: 'POST' });
    alert(`${res.message}`);
  }

  function viewCamera(id) {
    alert(`Placeholder stream viewer for camera ${id} (WebRTC/HLS TODO)`);
  }

  async function runDetection() {
    let payload = {};
    try { payload = JSON.parse(document.getElementById('detect-payload').value || '{}'); } catch {}
    const source = document.getElementById('detect-source').value || 'camera';
    const res = await api('/core/detect', { method: 'POST', body: JSON.stringify({ source, payload }) });
    showMsg('detect-result', res, 'success');
  }

  async function askAssistant() {
    const query = document.getElementById('assistant-query').value;
    const res = await api('/assistant/query', { method: 'POST', body: JSON.stringify({ query, context: {} }) });
    showMsg('assistant-result', res, 'success');
  }

  async function loadIncidents() {
    const items = await api('/incidents');
    const box = document.getElementById('incident-list');
    box.innerHTML = items.map((i) => `<div class="item-card">
      <strong>${i.type}</strong> | ${i.severity} | ${i.status}<br>
      ${i.description}<br>
      <button class="btn" onclick="assignIncident('${i.id}')">Assign Me</button>
      <button class="btn secondary" onclick="noteIncident('${i.id}')">Add Note</button>
      <button class="btn" onclick="closeIncident('${i.id}')">Close</button>
    </div>`).join('');
  }

  async function createIncident() {
    const payload = {
      type: document.getElementById('inc-type').value,
      severity: document.getElementById('inc-severity').value,
      site_id: document.getElementById('inc-site').value,
      camera_id: document.getElementById('inc-camera').value || null,
      description: document.getElementById('inc-desc').value,
    };
    await api('/incidents', { method: 'POST', body: JSON.stringify(payload) });
    await loadIncidents();
    await loadDashboard();
  }

  async function assignIncident(id) {
    await api(`/incidents/${id}/assign`, { method: 'POST', body: JSON.stringify({ user_id: state.user?.id }) });
    await loadIncidents();
  }

  async function noteIncident(id) {
    const note = prompt('Add note');
    if (!note) return;
    await api(`/incidents/${id}/notes`, { method: 'POST', body: JSON.stringify({ note }) });
    await loadIncidents();
  }

  async function closeIncident(id) {
    await api(`/incidents/${id}/close`, { method: 'POST' });
    await loadIncidents();
    await loadDashboard();
  }

  async function predictRisk() {
    const location = document.getElementById('risk-location').value;
    const historical_incidents = Number(document.getElementById('risk-historical').value || 0);
    const environmental_factors = (document.getElementById('risk-factors').value || '').split('\n').map((x) => x.trim()).filter(Boolean);
    const res = await api('/core/predict-risk', { method: 'POST', body: JSON.stringify({ location, historical_incidents, environmental_factors }) });
    showMsg('risk-result', res, 'success');
  }

  async function createRiskAssessment() {
    const payload = {
      hazard: document.getElementById('ra-hazard').value,
      likelihood: Number(document.getElementById('ra-likelihood').value || 1),
      severity: Number(document.getElementById('ra-severity').value || 1),
      controls: (document.getElementById('ra-controls').value || '').split(',').map((x) => x.trim()).filter(Boolean),
      residual_score: Number(document.getElementById('ra-residual').value || 1),
    };
    await api('/risk-assessments', { method: 'POST', body: JSON.stringify(payload) });
    alert('Risk assessment added');
  }

  async function loadPermits() {
    const items = await api('/core/work-permits');
    const box = document.getElementById('permit-list');
    box.innerHTML = items.map((p) => `<div class="item-card">
      <strong>${p.title}</strong> | ${p.risk_level} | ${p.status}<br>
      <button class="btn" onclick="updatePermitStatus('${p.id}','submitted')">Submit</button>
      <button class="btn" onclick="updatePermitStatus('${p.id}','approved')">Approve</button>
      <button class="btn secondary" onclick="updatePermitStatus('${p.id}','rejected')">Reject</button>
      <button class="btn secondary" onclick="updatePermitStatus('${p.id}','closed')">Close</button>
    </div>`).join('');
  }

  async function createPermit() {
    const payload = {
      title: document.getElementById('permit-title').value,
      site_id: document.getElementById('permit-site').value,
      risk_level: document.getElementById('permit-risk').value,
      approver: document.getElementById('permit-approver').value,
      checklist_items: (document.getElementById('permit-items').value || '').split('\n').map((x) => x.trim()).filter(Boolean),
    };
    await api('/core/work-permits', { method: 'POST', body: JSON.stringify(payload) });
    await loadPermits();
    await loadDashboard();
  }

  async function updatePermitStatus(id, status) {
    await api(`/core/work-permits/${id}`, { method: 'PUT', body: JSON.stringify({ status }) });
    await loadPermits();
    await loadDashboard();
  }

  async function runBehavior() {
    const location = document.getElementById('behavior-location').value;
    const events = JSON.parse(document.getElementById('behavior-events').value || '[]');
    const res = await api('/core/behavior-analysis', { method: 'POST', body: JSON.stringify({ location, events }) });
    showMsg('behavior-result', res, res.flagged ? 'error' : 'success');
  }

  async function loadInspections() {
    const items = await api('/inspections');
    const box = document.getElementById('inspection-list');
    box.innerHTML = items.map((i) => `<div class="item-card">Score: ${i.score} | Findings: ${(i.findings || []).join('; ')}</div>`).join('');
  }

  async function createInspection() {
    const payload = {
      template_id: null,
      score: Number(document.getElementById('insp-score').value || 0),
      findings: (document.getElementById('insp-findings').value || '').split('\n').map((x) => x.trim()).filter(Boolean),
      attachments: [],
    };
    await api('/inspections', { method: 'POST', body: JSON.stringify(payload) });
    await loadInspections();
  }

  async function loadPage(page) {
    try {
      if (!state.token && page !== 'dashboard') return;
      if (page === 'dashboard') await loadDashboard();
      if (page === 'cameras') await loadCameras();
      if (page === 'incidents') await loadIncidents();
      if (page === 'permits') await loadPermits();
      if (page === 'inspections') await loadInspections();
    } catch (e) {
      console.error(e);
    }
  }

  function bind() {
    document.querySelectorAll('.nav-item').forEach((a) => a.addEventListener('click', (e) => {
      e.preventDefault();
      activatePage(a.dataset.page);
    }));
    document.getElementById('login-btn').addEventListener('click', login);
    document.getElementById('seed-btn').addEventListener('click', runSeed);
  }

  setAuthUI();
  bind();
  activatePage('dashboard');

  window.createCamera = createCamera;
  window.testCamera = testCamera;
  window.viewCamera = viewCamera;
  window.runDetection = runDetection;
  window.askAssistant = askAssistant;
  window.createIncident = createIncident;
  window.assignIncident = assignIncident;
  window.noteIncident = noteIncident;
  window.closeIncident = closeIncident;
  window.predictRisk = predictRisk;
  window.createRiskAssessment = createRiskAssessment;
  window.createPermit = createPermit;
  window.updatePermitStatus = updatePermitStatus;
  window.runBehavior = runBehavior;
  window.createInspection = createInspection;
})();
