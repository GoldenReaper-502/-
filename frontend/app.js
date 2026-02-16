(() => {
  const API_BASE_URL =
    (window.location.port === '4173' && (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'))
      ? 'http://127.0.0.1:8000/api'
      : '/api';

  const state = {
    chart: null,
    openapi: null,
  };

  const el = {
    tabs: document.querySelectorAll('.tab'),
    panels: document.querySelectorAll('.panel'),
    kpiRisk: document.getElementById('kpi-risk'),
    kpiPermits: document.getElementById('kpi-permits'),
    kpiAlerts: document.getElementById('kpi-alerts'),
    kpiSystem: document.getElementById('kpi-system'),
    riskForm: document.getElementById('risk-form'),
    riskResult: document.getElementById('risk-result'),
    behaviorForm: document.getElementById('behavior-form'),
    behaviorResult: document.getElementById('behavior-result'),
    permitForm: document.getElementById('permit-form'),
    permitsList: document.getElementById('permits-list'),
    toast: document.getElementById('toast'),
  };

  function notify(message, isError = false) {
    el.toast.textContent = message;
    el.toast.style.background = isError ? '#6b2332' : '#1e2e57';
    el.toast.classList.add('show');
    setTimeout(() => el.toast.classList.remove('show'), 2400);
  }

  async function request(path, options = {}) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method || 'GET',
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    let json = {};
    try {
      json = await res.json();
    } catch (_) {}

    if (!res.ok) {
      throw new Error(json.detail || `HTTP ${res.status}`);
    }
    return json;
  }

  async function loadOpenApi() {
    if (state.openapi) return state.openapi;
    try {
      state.openapi = await request('/openapi.json');
      return state.openapi;
    } catch {
      state.openapi = { paths: {} };
      return state.openapi;
    }
  }

  async function resolvePath(candidates) {
    const schema = await loadOpenApi();
    const paths = new Set(Object.keys(schema.paths || {}));
    return candidates.find((c) => paths.has(c)) || candidates[0];
  }

  async function checkSystem() {
    try {
      const path = await resolvePath(['/core/system/status', '/system/status']);
      const data = await request(path);
      el.kpiSystem.textContent = data.healthy || data.status === 'ok' ? 'Online' : 'Degraded';
    } catch (error) {
      el.kpiSystem.textContent = 'Offline';
      notify(`System check failed: ${error.message}`, true);
    }
  }

  function renderRiskChart(reports = []) {
    const ctx = document.getElementById('risk-chart');
    if (!ctx) return;

    const labels = reports.length ? reports.map((r) => r.label || r.month || '-') : ['Jan', 'Feb', 'Mar'];
    const values = reports.length ? reports.map((r) => r.value || r.score || 0) : [45, 55, 62];

    if (state.chart) state.chart.destroy();

    state.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Risk Score',
            data: values,
            borderColor: '#4d7bff',
            backgroundColor: 'rgba(77,123,255,0.18)',
            fill: true,
            tension: 0.32,
          },
        ],
      },
      options: { responsive: true, plugins: { legend: { labels: { color: '#e6edff' } } } },
    });
  }

  async function loadDashboard() {
    try {
      const path = await resolvePath(['/dashboard']);
      const data = await request(path);
      el.kpiRisk.textContent = data.risk_score ?? data.totals?.risk_score ?? 0;
      el.kpiPermits.textContent = data.active_permits ?? 0;
      el.kpiAlerts.textContent = data.smart_alerts ?? data.totals?.detections ?? 0;
      renderRiskChart(data.reports || []);
    } catch (error) {
      notify(`Dashboard failed: ${error.message}`, true);
    }
  }

  async function loadPermits() {
    try {
      const path = await resolvePath(['/core/work-permits']);
      const permits = await request(path);
      el.permitsList.innerHTML = permits
        .map(
          (p) => `<div class="permit-item"><strong>${p.title}</strong><br/>${p.risk_level} | ${p.status}<br/>Approved by: ${p.approved_by}</div>`
        )
        .join('');
    } catch (error) {
      notify(`Permits failed: ${error.message}`, true);
    }
  }

  async function submitRisk(event) {
    event.preventDefault();
    const fd = new FormData(el.riskForm);
    const payload = {
      location: fd.get('location'),
      historical_incidents: Number(fd.get('historical_incidents') || 0),
      environmental_factors: String(fd.get('environmental_factors') || '')
        .split(',')
        .map((x) => x.trim())
        .filter(Boolean),
    };

    try {
      const path = await resolvePath(['/core/predict-risk']);
      const data = await request(path, { method: 'POST', body: payload });
      el.riskResult.textContent = JSON.stringify(data, null, 2);
      notify('Risk prediction completed');
    } catch (error) {
      el.riskResult.textContent = error.message;
      notify(`Risk prediction failed: ${error.message}`, true);
    }
  }

  async function submitBehavior(event) {
    event.preventDefault();
    const fd = new FormData(el.behaviorForm);

    let events = [];
    try {
      events = JSON.parse(String(fd.get('events') || '[]'));
    } catch {
      notify('Invalid events JSON', true);
      return;
    }

    try {
      const path = await resolvePath(['/core/behavior-analysis']);
      const data = await request(path, {
        method: 'POST',
        body: {
          location: fd.get('location'),
          events,
        },
      });
      el.behaviorResult.textContent = JSON.stringify(data, null, 2);
      notify('Behavior analysis completed');
    } catch (error) {
      el.behaviorResult.textContent = error.message;
      notify(`Behavior analysis failed: ${error.message}`, true);
    }
  }

  async function submitPermit(event) {
    event.preventDefault();
    const fd = new FormData(el.permitForm);
    const payload = {
      title: fd.get('title'),
      risk_level: fd.get('risk_level'),
      approved_by: fd.get('approved_by'),
      status: fd.get('status'),
      checklist_items: String(fd.get('checklist_items') || '')
        .split(',')
        .map((x) => x.trim())
        .filter(Boolean),
    };

    try {
      const path = await resolvePath(['/core/work-permits']);
      await request(path, { method: 'POST', body: payload });
      el.permitForm.reset();
      await loadPermits();
      await loadDashboard();
      notify('Permit created successfully');
    } catch (error) {
      notify(`Create permit failed: ${error.message}`, true);
    }
  }

  function setupTabs() {
    el.tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        el.tabs.forEach((t) => t.classList.remove('active'));
        tab.classList.add('active');
        const target = tab.dataset.tab;
        el.panels.forEach((p) => p.classList.toggle('active', p.id === target));
      });
    });
  }

  async function init() {
    setupTabs();
    el.riskForm.addEventListener('submit', submitRisk);
    el.behaviorForm.addEventListener('submit', submitBehavior);
    el.permitForm.addEventListener('submit', submitPermit);

    await Promise.all([checkSystem(), loadDashboard(), loadPermits()]);
  }

  init();
})();
