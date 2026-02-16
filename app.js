const STORAGE_KEY = 'system-monitor-history-v1';
const LANG_KEY = 'system-monitor-lang-v1';

const translations = {
  ar: {
    dir: 'rtl',
    htmlLang: 'ar',
    pageTitle: 'Control Center | لوحة جاهزية النظام',
    badge: 'برنامج جاهز للتشغيل',
    title: 'لوحة جاهزية النظام',
    subtitle: 'متابعة حالة الـ Backend والـ Frontend مع فحص تلقائي، سجل زمني، وتصدير النتائج.',
    kpiLastCheck: 'آخر فحص',
    kpiNetwork: 'وضع الاتصال',
    kpiOverall: 'الحالة العامة',
    runCheck: 'تشغيل فحص الآن',
    startAuto: 'تشغيل الفحص التلقائي',
    stopAuto: 'إيقاف الفحص التلقائي',
    clearHistory: 'مسح السجل',
    intervalLabel: 'فترة التحديث (ثانية)',
    exportTypeLabel: 'نوع التصدير',
    languageLabel: 'اللغة',
    exportData: 'تصدير السجل',
    backendDesc: 'فحص API + Database + Auth بشكل محاكي.',
    frontendDesc: 'فحص Rendering + Routing + Assets بشكل محاكي.',
    latencyLabel: 'الاستجابة',
    lastMessageLabel: 'آخر رسالة',
    smartSummary: 'الملخص الذكي',
    historyTitle: 'سجل الفحوصات',
    thTime: 'الوقت',
    thService: 'الخدمة',
    thStatus: 'الحالة',
    thLatency: 'الاستجابة',
    thMessage: 'الرسالة',
    networkOnline: 'متصل',
    networkOffline: 'غير متصل',
    overallUnknown: 'غير محددة',
    overallStable: 'مستقر',
    overallMedium: 'متوسط',
    overallCritical: 'حرج',
    statusPending: 'قيد الفحص',
    statusWaiting: 'قيد الانتظار',
    statusReady: 'جاهز',
    statusFailed: 'متعثر',
    summaryInitial: 'اضغط "تشغيل فحص الآن" لبدء التقييم.',
    summaryAllOk: 'ممتاز ✅: كل الخدمات تعمل ضمن المعدل الطبيعي.',
    summaryOneOk: 'تنبيه ⚠️: خدمة واحدة تعمل وأخرى تحتاج متابعة.',
    summaryAllFail: 'مشكلة ❌: الخدمتان متعثرتان، راجع السجل للتفاصيل.',
    noDataToExport: 'لا توجد بيانات لتصديرها بعد.',
    countResults: (n) => `${n} نتائج`,
    serviceBackend: 'Backend',
    serviceFrontend: 'Frontend',
    messageNotStarted: 'لم يبدأ الفحص',
    backendSuccessMessages: ['API متاح', 'Auth تعمل', 'قاعدة البيانات متصلة'],
    frontendSuccessMessages: ['الواجهة ترسم بنجاح', 'المسارات تعمل', 'الأصول static متاحة'],
    reviewWarning: (name) => `تحذير: ${name} يحتاج مراجعة.`,
  },
  en: {
    dir: 'ltr',
    htmlLang: 'en',
    pageTitle: 'Control Center | System Readiness Dashboard',
    badge: 'Ready-to-run Program',
    title: 'System Readiness Dashboard',
    subtitle: 'Track Backend and Frontend status with auto checks, history log, and exports.',
    kpiLastCheck: 'Last Check',
    kpiNetwork: 'Network',
    kpiOverall: 'Overall State',
    runCheck: 'Run Check Now',
    startAuto: 'Start Auto Check',
    stopAuto: 'Stop Auto Check',
    clearHistory: 'Clear History',
    intervalLabel: 'Refresh Interval (sec)',
    exportTypeLabel: 'Export Type',
    languageLabel: 'Language',
    exportData: 'Export History',
    backendDesc: 'Simulated API + Database + Auth health check.',
    frontendDesc: 'Simulated Rendering + Routing + Assets health check.',
    latencyLabel: 'Latency',
    lastMessageLabel: 'Last Message',
    smartSummary: 'Smart Summary',
    historyTitle: 'Check History',
    thTime: 'Time',
    thService: 'Service',
    thStatus: 'Status',
    thLatency: 'Latency',
    thMessage: 'Message',
    networkOnline: 'Online',
    networkOffline: 'Offline',
    overallUnknown: 'Unknown',
    overallStable: 'Stable',
    overallMedium: 'Degraded',
    overallCritical: 'Critical',
    statusPending: 'Checking',
    statusWaiting: 'Waiting',
    statusReady: 'Ready',
    statusFailed: 'Failed',
    summaryInitial: 'Press "Run Check Now" to start evaluation.',
    summaryAllOk: 'Excellent ✅: all services are healthy.',
    summaryOneOk: 'Warning ⚠️: one service is healthy and one needs attention.',
    summaryAllFail: 'Issue ❌: both services are failing, check history for details.',
    noDataToExport: 'No data available to export yet.',
    countResults: (n) => `${n} results`,
    serviceBackend: 'Backend',
    serviceFrontend: 'Frontend',
    messageNotStarted: 'No checks have run yet',
    backendSuccessMessages: ['API reachable', 'Auth is healthy', 'Database connected'],
    frontendSuccessMessages: ['UI rendered successfully', 'Routes are working', 'Static assets are available'],
    reviewWarning: (name) => `Warning: ${name} needs review.`,
  },
};

let currentLang = localStorage.getItem(LANG_KEY) || 'ar';
if (!translations[currentLang]) currentLang = 'ar';

const ui = {
  runCheck: document.getElementById('run-check'),
  toggleAuto: document.getElementById('toggle-auto'),
  clearHistory: document.getElementById('clear-history'),
  intervalInput: document.getElementById('interval-input'),
  exportType: document.getElementById('export-type'),
  exportData: document.getElementById('export-data'),
  languageSelect: document.getElementById('language-select'),
  summary: document.getElementById('summary-text'),
  lastCheck: document.getElementById('last-check'),
  networkState: document.getElementById('network-state'),
  overallState: document.getElementById('overall-state'),
  historyBody: document.getElementById('history-body'),
  historyCount: document.getElementById('history-count'),
};

const serviceViews = {
  backend: {
    status: document.getElementById('backend-status'),
    latency: document.getElementById('backend-latency'),
    message: document.getElementById('backend-message'),
  },
  frontend: {
    status: document.getElementById('frontend-status'),
    latency: document.getElementById('frontend-latency'),
    message: document.getElementById('frontend-message'),
  },
};

let history = readHistory();
let autoTimer = null;

function t() {
  return translations[currentLang];
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function formatTime(date = new Date()) {
  return date.toLocaleString(currentLang === 'ar' ? 'ar-SA' : 'en-US', { hour12: false });
}

function applyI18nText() {
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.dataset.i18n;
    if (t()[key]) el.textContent = t()[key];
  });
}

function applyLanguage() {
  document.documentElement.lang = t().htmlLang;
  document.documentElement.dir = t().dir;
  document.title = t().pageTitle;
  ui.languageSelect.value = currentLang;

  applyI18nText();

  if (ui.summary.dataset.state === 'initial') {
    ui.summary.textContent = t().summaryInitial;
  }

  updateNetworkState();
  updateAutoButtonText();
  renderHistory();

  if (ui.overallState.dataset.state === 'unknown') {
    ui.overallState.textContent = t().overallUnknown;
  }

  if (serviceViews.backend.message.dataset.state === 'not-started') {
    serviceViews.backend.message.textContent = t().messageNotStarted;
    serviceViews.frontend.message.textContent = t().messageNotStarted;
  }
}

function simulateCheck(serviceKey) {
  const successMessages = serviceKey === 'backend' ? t().backendSuccessMessages : t().frontendSuccessMessages;
  const latencyMs = randomInt(60, 950);
  const isOk = Math.random() > 0.15;
  const serviceName = serviceKey === 'backend' ? t().serviceBackend : t().serviceFrontend;
  const message = isOk
    ? successMessages[randomInt(0, successMessages.length - 1)]
    : t().reviewWarning(serviceName);

  return {
    ok: isOk,
    latencyMs,
    message,
  };
}

function setStatus(el, ok, pending = false) {
  el.classList.remove('pending', 'success', 'fail');

  if (pending) {
    el.textContent = t().statusPending;
    el.classList.add('pending');
    return;
  }

  el.textContent = ok ? t().statusReady : t().statusFailed;
  el.classList.add(ok ? 'success' : 'fail');
}

function appendHistoryRow(item) {
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>${item.time}</td>
    <td>${item.service}</td>
    <td>${item.ok ? t().statusReady : t().statusFailed}</td>
    <td>${item.latencyMs} ms</td>
    <td>${item.message}</td>
  `;
  ui.historyBody.append(tr);
}

function renderHistory() {
  ui.historyBody.innerHTML = '';
  history.forEach(appendHistoryRow);
  ui.historyCount.textContent = t().countResults(history.length);
}

function persistHistory() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

function readHistory() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function updateNetworkState() {
  ui.networkState.textContent = navigator.onLine ? t().networkOnline : t().networkOffline;
}

function updateSummary(backend, frontend) {
  ui.summary.dataset.state = 'dynamic';
  const allOk = backend.ok && frontend.ok;
  const oneOk = backend.ok || frontend.ok;

  if (allOk) {
    ui.overallState.dataset.state = 'stable';
    ui.overallState.textContent = t().overallStable;
    ui.summary.textContent = t().summaryAllOk;
    return;
  }

  if (oneOk) {
    ui.overallState.dataset.state = 'medium';
    ui.overallState.textContent = t().overallMedium;
    ui.summary.textContent = t().summaryOneOk;
    return;
  }

  ui.overallState.dataset.state = 'critical';
  ui.overallState.textContent = t().overallCritical;
  ui.summary.textContent = t().summaryAllFail;
}

function runChecks() {
  setStatus(serviceViews.backend.status, false, true);
  setStatus(serviceViews.frontend.status, false, true);

  const backendResult = simulateCheck('backend');
  const frontendResult = simulateCheck('frontend');

  serviceViews.backend.latency.textContent = `${backendResult.latencyMs} ms`;
  serviceViews.backend.message.dataset.state = 'dynamic';
  serviceViews.backend.message.textContent = backendResult.message;
  setStatus(serviceViews.backend.status, backendResult.ok);

  serviceViews.frontend.latency.textContent = `${frontendResult.latencyMs} ms`;
  serviceViews.frontend.message.dataset.state = 'dynamic';
  serviceViews.frontend.message.textContent = frontendResult.message;
  setStatus(serviceViews.frontend.status, frontendResult.ok);

  const time = formatTime();
  ui.lastCheck.textContent = time;

  const records = [
    { time, service: t().serviceBackend, ...backendResult },
    { time, service: t().serviceFrontend, ...frontendResult },
  ];

  history = [...records, ...history].slice(0, 100);
  persistHistory();
  renderHistory();
  updateSummary(backendResult, frontendResult);
}

function updateAutoButtonText() {
  if (autoTimer) {
    const seconds = Number(ui.intervalInput.value) || 20;
    ui.toggleAuto.textContent = `${t().stopAuto} (${seconds}s)`;
  } else {
    ui.toggleAuto.textContent = t().startAuto;
  }
}

function toggleAutoChecks() {
  if (autoTimer) {
    clearInterval(autoTimer);
    autoTimer = null;
    updateAutoButtonText();
    return;
  }

  const seconds = Number(ui.intervalInput.value) || 20;
  const safeSeconds = Math.min(Math.max(seconds, 5), 300);
  ui.intervalInput.value = String(safeSeconds);

  autoTimer = setInterval(runChecks, safeSeconds * 1000);
  updateAutoButtonText();
}

function clearHistory() {
  history = [];
  persistHistory();
  renderHistory();
}

function exportHistory() {
  const type = ui.exportType.value;

  if (!history.length) {
    ui.summary.dataset.state = 'dynamic';
    ui.summary.textContent = t().noDataToExport;
    return;
  }

  let content = '';
  let mime = '';
  let ext = '';

  if (type === 'csv') {
    ext = 'csv';
    mime = 'text/csv;charset=utf-8';
    const header = 'time,service,status,latencyMs,message';
    const rows = history.map((r) =>
      [r.time, r.service, r.ok ? 'ready' : 'failed', r.latencyMs, JSON.stringify(r.message)].join(',')
    );
    content = [header, ...rows].join('\n');
  } else {
    ext = 'json';
    mime = 'application/json;charset=utf-8';
    content = JSON.stringify(history, null, 2);
  }

  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `system-monitor-history.${ext}`;
  a.click();
  URL.revokeObjectURL(url);
}

function changeLanguage(newLang) {
  if (!translations[newLang]) return;
  currentLang = newLang;
  localStorage.setItem(LANG_KEY, currentLang);
  applyLanguage();
}

ui.runCheck.addEventListener('click', runChecks);
ui.toggleAuto.addEventListener('click', toggleAutoChecks);
ui.clearHistory.addEventListener('click', clearHistory);
ui.exportData.addEventListener('click', exportHistory);
ui.languageSelect.addEventListener('change', (event) => changeLanguage(event.target.value));

window.addEventListener('online', updateNetworkState);
window.addEventListener('offline', updateNetworkState);

ui.summary.dataset.state = 'initial';
ui.overallState.dataset.state = 'unknown';
serviceViews.backend.message.dataset.state = 'not-started';
serviceViews.frontend.message.dataset.state = 'not-started';

serviceViews.backend.status.textContent = t().statusWaiting;
serviceViews.frontend.status.textContent = t().statusWaiting;
serviceViews.backend.message.textContent = t().messageNotStarted;
serviceViews.frontend.message.textContent = t().messageNotStarted;

applyLanguage();
