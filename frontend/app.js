(() => {
  'use strict';

  const DEFAULT_DEV_API = 'http://127.0.0.1:8000/api';

  function computeApiBaseUrl() {
    if (window.__APP_CONFIG__?.API_BASE_URL) return window.__APP_CONFIG__.API_BASE_URL;

    const saved = localStorage.getItem('hazm_api_base_url');
    if (saved) return saved;

    const { protocol, hostname, port } = window.location;
    const isLocal4173 = (hostname === '127.0.0.1' || hostname === 'localhost') && port === '4173';

    if (isLocal4173) return DEFAULT_DEV_API;

    return '/api';
  }

  const CONFIG = {
    API_BASE_URL: computeApiBaseUrl(),
    REQUEST_TIMEOUT_MS: 15000,
  };

  const state = {
    openApiLoaded: false,
    openApiPaths: new Set(),
    lastErrors: [],
  };

  const ENDPOINTS = {
    platformInfo: ['/platform/info'],
    systemStatus: ['/core/system/status', '/system/status', '/platform/info'],
    detect: ['/core/detect', '/detect'],
    chat: ['/core/chat', '/chat'],
    incidentCreate: ['/core/incident', '/incident'],
    nearMissCreate: ['/core/near-miss', '/near-miss'],
    dashboard: ['/dashboard', '/core/dashboard'],
    incidentList: ['/core/incident', '/incidents', '/incident'],
    reports: ['/dashboard/reports', '/reports'],
  };

  const ui = {
    networkState: document.getElementById('network-state'),
    overallState: document.getElementById('overall-state'),
    summary: document.getElementById('summary-text'),
    backendStatus: document.getElementById('backend-status'),
    backendLatency: document.getElementById('backend-latency'),
    backendMessage: document.getElementById('backend-message'),
    frontendStatus: document.getElementById('frontend-status'),
    frontendLatency: document.getElementById('frontend-latency'),
    frontendMessage: document.getElementById('frontend-message'),
    historyBody: document.getElementById('history-body'),
    historyCount: document.getElementById('history-count'),
    runCheckButton: document.getElementById('run-check'),
  };

  function setText(el, value) {
    if (!el) return;
    el.textContent = value;
  }

  function setStatusBadge(el, statusText, className) {
    if (!el) return;
    el.classList.remove('pending', 'success', 'fail');
    if (className) el.classList.add(className);
    el.textContent = statusText;
  }

  function rememberError(message) {
    state.lastErrors.unshift({ message, at: new Date().toISOString() });
    state.lastErrors = state.lastErrors.slice(0, 20);
    console.warn('[API]', message);
  }

  function normalizeBaseUrl(url) {
    return url.replace(/\/+$/, '');
  }

  function buildUrl(path) {
    const base = normalizeBaseUrl(CONFIG.API_BASE_URL);
    const cleanPath = path.startsWith('/') ? path : `/${path}`;
    return `${base}${cleanPath}`;
  }

  function withTimeout(promise, timeoutMs = CONFIG.REQUEST_TIMEOUT_MS) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);

    return {
      signal: controller.signal,
      wait: promise(controller.signal)
        .finally(() => clearTimeout(timeout)),
    };
  }

  async function apiRequest(path, options = {}) {
    const url = buildUrl(path);
    const startedAt = performance.now();

    const { signal, wait } = withTimeout(async (timeoutSignal) => {
      const response = await fetch(url, {
        method: options.method || 'GET',
        headers: {
          'Content-Type': options.body instanceof FormData ? undefined : 'application/json',
          ...(options.headers || {}),
        },
        body:
          options.body == null
            ? undefined
            : options.body instanceof FormData
              ? options.body
              : JSON.stringify(options.body),
        signal: timeoutSignal,
      });

      const latencyMs = Math.round(performance.now() - startedAt);
      const text = await response.text();
      let parsed;
      try {
        parsed = text ? JSON.parse(text) : {};
      } catch {
        parsed = { raw: text };
      }

      if (!response.ok) {
        const message = parsed?.detail || parsed?.message || `HTTP ${response.status}`;
        const error = new Error(message);
        error.status = response.status;
        error.response = parsed;
        throw error;
      }

      return { data: parsed, latencyMs };
    });

    try {
      return await wait;
    } catch (error) {
      if (signal.aborted) {
        error.message = `Request timeout after ${CONFIG.REQUEST_TIMEOUT_MS}ms (${path})`;
      }
      throw error;
    }
  }

  async function loadOpenAPI() {
    if (state.openApiLoaded) return;

    try {
      const { data } = await apiRequest('/openapi.json');
      const paths = Object.keys(data?.paths || {});
      state.openApiPaths = new Set(paths);
      state.openApiLoaded = true;
    } catch (error) {
      rememberError(`Unable to load OpenAPI schema: ${error.message}`);
      state.openApiLoaded = true;
    }
  }

  function endpointExists(path) {
    if (!state.openApiPaths.size) return false;
    return state.openApiPaths.has(path);
  }

  function resolveEndpoint(candidates = []) {
    const existing = candidates.find((path) => endpointExists(path));
    return existing || candidates[0];
  }

  function pickFirst(...values) {
    for (const value of values) {
      if (value !== undefined && value !== null) return value;
    }
    return null;
  }

  function asArray(value) {
    if (Array.isArray(value)) return value;
    if (Array.isArray(value?.items)) return value.items;
    if (Array.isArray(value?.results)) return value.results;
    if (Array.isArray(value?.incidents)) return value.incidents;
    if (Array.isArray(value?.data)) return value.data;
    return [];
  }

  function toFriendlyError(error, fallback) {
    return error?.message || error?.detail || fallback;
  }

  async function checkSystemStatus() {
    await loadOpenAPI();
    const endpoint = resolveEndpoint(ENDPOINTS.systemStatus);
    try {
      const { data, latencyMs } = await apiRequest(endpoint);
      const healthy = pickFirst(data?.healthy, data?.status === 'ok', data?.ok, true);
      const message = pickFirst(data?.message, data?.detail, 'System status loaded.');

      return {
        ok: Boolean(healthy),
        latencyMs,
        message,
        raw: data,
      };
    } catch (error) {
      const fallbackMessage = `Failed to check system status (${endpoint})`;
      return {
        ok: false,
        latencyMs: null,
        message: toFriendlyError(error, fallbackMessage),
        raw: null,
      };
    }
  }

  async function detectObjects(payload) {
    await loadOpenAPI();
    const endpoint = resolveEndpoint(ENDPOINTS.detect);

    try {
      const { data, latencyMs } = await apiRequest(endpoint, {
        method: 'POST',
        body: payload,
      });

      return {
        ok: true,
        latencyMs,
        detections: asArray(data?.detections || data),
        raw: data,
      };
    } catch (error) {
      return {
        ok: false,
        latencyMs: null,
        detections: [],
        error: toFriendlyError(error, `Detection request failed (${endpoint})`),
      };
    }
  }

  async function sendChat(payload) {
    await loadOpenAPI();
    const endpoint = resolveEndpoint(ENDPOINTS.chat);

    try {
      const { data, latencyMs } = await apiRequest(endpoint, {
        method: 'POST',
        body: payload,
      });

      return {
        ok: true,
        latencyMs,
        reply: pickFirst(data?.reply, data?.response, data?.message, ''),
        raw: data,
      };
    } catch (error) {
      return {
        ok: false,
        latencyMs: null,
        reply: '',
        error: toFriendlyError(error, `Chat request failed (${endpoint})`),
      };
    }
  }

  async function createIncident(payload) {
    await loadOpenAPI();
    const endpoint = resolveEndpoint(ENDPOINTS.incidentCreate);

    try {
      const { data, latencyMs } = await apiRequest(endpoint, {
        method: 'POST',
        body: payload,
      });
      return { ok: true, latencyMs, data };
    } catch (error) {
      return { ok: false, latencyMs: null, error: toFriendlyError(error, `Incident create failed (${endpoint})`) };
    }
  }

  async function createNearMiss(payload) {
    await loadOpenAPI();
    const endpoint = resolveEndpoint(ENDPOINTS.nearMissCreate);

    try {
      const { data, latencyMs } = await apiRequest(endpoint, {
        method: 'POST',
        body: payload,
      });
      return { ok: true, latencyMs, data };
    } catch (error) {
      return { ok: false, latencyMs: null, error: toFriendlyError(error, `Near-miss create failed (${endpoint})`) };
    }
  }

  async function loadDashboard() {
    await loadOpenAPI();
    const endpoint = resolveEndpoint(ENDPOINTS.dashboard);

    try {
      const { data } = await apiRequest(endpoint);

      return {
        ok: true,
        totals: {
          incidents: pickFirst(data?.totals?.incidents, data?.incidents_count, asArray(data?.incidents).length, 0),
          nearMisses: pickFirst(data?.totals?.near_misses, data?.near_miss_count, asArray(data?.near_misses).length, 0),
          detections: pickFirst(data?.totals?.detections, data?.detections_count, asArray(data?.detections).length, 0),
        },
        incidents: asArray(data?.incidents),
        reports: asArray(data?.reports),
        raw: data,
      };
    } catch (error) {
      const fallback = await Promise.allSettled([loadIncidents(), loadReports()]);
      const incidentsResult = fallback[0].status === 'fulfilled' ? fallback[0].value : { incidents: [] };
      const reportsResult = fallback[1].status === 'fulfilled' ? fallback[1].value : { reports: [] };

      return {
        ok: false,
        incidents: incidentsResult.incidents || [],
        reports: reportsResult.reports || [],
        totals: {
          incidents: (incidentsResult.incidents || []).length,
          nearMisses: 0,
          detections: 0,
        },
        error: toFriendlyError(error, `Dashboard endpoint unavailable (${endpoint})`),
      };
    }
  }

  async function loadIncidents() {
    await loadOpenAPI();
    const endpoint = resolveEndpoint(ENDPOINTS.incidentList);

    try {
      const { data } = await apiRequest(endpoint);
      return {
        ok: true,
        incidents: asArray(data?.incidents || data),
        raw: data,
      };
    } catch (error) {
      return {
        ok: false,
        incidents: [],
        error: toFriendlyError(error, `Incidents load failed (${endpoint})`),
      };
    }
  }

  async function loadReports() {
    await loadOpenAPI();
    const endpoint = resolveEndpoint(ENDPOINTS.reports);

    try {
      const { data } = await apiRequest(endpoint);
      return {
        ok: true,
        reports: asArray(data?.reports || data),
        raw: data,
      };
    } catch (error) {
      return {
        ok: false,
        reports: [],
        error: toFriendlyError(error, `Reports load failed (${endpoint})`),
      };
    }
  }

  function addHistoryRow(service, ok, latencyMs, message) {
    if (!ui.historyBody) return;
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${new Date().toLocaleTimeString()}</td>
      <td>${service}</td>
      <td>${ok ? 'جاهز' : 'متعثر'}</td>
      <td>${latencyMs == null ? '—' : `${latencyMs} ms`}</td>
      <td>${message}</td>
    `;
    ui.historyBody.prepend(row);

    if (ui.historyCount) {
      const rows = ui.historyBody.querySelectorAll('tr').length;
      ui.historyCount.textContent = `${rows} نتائج`;
    }
  }

  async function runConnectivityCheck() {
    setText(ui.networkState, navigator.onLine ? 'متصل' : 'غير متصل');

    const result = await checkSystemStatus();
    const backendOk = result.ok;

    setStatusBadge(ui.backendStatus, backendOk ? 'جاهز' : 'متعثر', backendOk ? 'success' : 'fail');
    setText(ui.backendLatency, result.latencyMs == null ? '—' : `${result.latencyMs} ms`);
    setText(ui.backendMessage, result.message);

    setStatusBadge(ui.frontendStatus, 'جاهز', 'success');
    setText(ui.frontendLatency, '0 ms');
    setText(ui.frontendMessage, 'Frontend loaded successfully.');

    if (backendOk) {
      setText(ui.overallState, 'مستقر');
      setText(ui.summary, 'الاتصال بالباك اند ناجح ✅');
    } else {
      setText(ui.overallState, 'متوسط');
      setText(ui.summary, `تعذر الاتصال ببعض الخدمات: ${result.message}`);
    }

    addHistoryRow('Backend', backendOk, result.latencyMs, result.message);
  }

  async function init() {
    await loadOpenAPI();
    await runConnectivityCheck();

    ui.runCheckButton?.addEventListener('click', runConnectivityCheck);

    window.addEventListener('online', runConnectivityCheck);
    window.addEventListener('offline', runConnectivityCheck);
  }

  window.AppAPI = {
    CONFIG,
    checkSystemStatus,
    detectObjects,
    sendChat,
    createIncident,
    createNearMiss,
    loadDashboard,
    loadIncidents,
    loadReports,
    setApiBaseUrl(url) {
      CONFIG.API_BASE_URL = normalizeBaseUrl(url);
      localStorage.setItem('hazm_api_base_url', CONFIG.API_BASE_URL);
      return CONFIG.API_BASE_URL;
    },
    getErrors() {
      return [...state.lastErrors];
    },
  };

  init();
})();
