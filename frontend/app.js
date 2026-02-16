const CONFIG = {
  API_BASE_URL: "http://127.0.0.1:8000/api",
};

const state = {
  chart: null,
  currentPage: "dashboard",
};

function getApiBaseUrl() {
  const onLocal4173 =
    window.location.port === "4173" &&
    (window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost");
  return onLocal4173 ? "http://127.0.0.1:8000/api" : "/api";
}

CONFIG.API_BASE_URL = getApiBaseUrl();

async function apiFetch(path, options = {}) {
  const response = await fetch(`${CONFIG.API_BASE_URL}${path}`, {
    method: options.method || "GET",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    body: options.body,
  });

  let data = {};
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    throw new Error(data.message || data.detail || `HTTP ${response.status}`);
  }

  return data;
}

function showPage(pageName) {
  document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach((n) => n.classList.remove("active"));

  const page = document.getElementById(`${pageName}Page`);
  if (page) page.classList.add("active");

  const nav = document.querySelector(`[data-page="${pageName}"]`);
  if (nav) nav.classList.add("active");

  state.currentPage = pageName;
  loadPageData(pageName);
}

async function loadDashboardAdvanced() {
  try {
    const [permits, checklists, dashboard] = await Promise.all([
      apiFetch("/core/work-permits").catch(() => []),
      apiFetch("/core/checklists").catch(() => []),
      apiFetch("/dashboard").catch(() => ({})),
    ]);

    const activePermits = permits.filter((p) => (p.status || "").toLowerCase() === "active").length;
    const riskScore = dashboard.risk_score ??
      (permits.length
        ? Math.round(
            permits.reduce(
              (acc, p) => acc + (p.risk_level === "High" ? 80 : p.risk_level === "Medium" ? 50 : 20),
              0
            ) / permits.length
          )
        : 0);

    const smartAlerts = dashboard.smart_alerts ?? permits.filter((p) => p.risk_level !== "Low").length;

    const globalRiskScore = document.getElementById("globalRiskScore");
    const activePermitsCount = document.getElementById("activePermitsCount");
    const checklistsCount = document.getElementById("checklistsCount");
    const systemHealth = document.getElementById("systemHealth");

    if (globalRiskScore) globalRiskScore.textContent = String(riskScore);
    if (activePermitsCount) activePermitsCount.textContent = String(activePermits);
    if (checklistsCount) checklistsCount.textContent = String(checklists.length);
    if (systemHealth) systemHealth.textContent = smartAlerts >= 1 ? "Online" : "Monitoring";

    const ctx = document.getElementById("dashboardChart");
    if (ctx && window.Chart) {
      if (state.chart) state.chart.destroy();

      const buckets = { Low: 0, Medium: 0, High: 0 };
      permits.forEach((p) => {
        const level = p.risk_level in buckets ? p.risk_level : "Medium";
        buckets[level] += 1;
      });

      state.chart = new Chart(ctx, {
        type: "bar",
        data: {
          labels: ["Low", "Medium", "High"],
          datasets: [
            {
              label: "Work Permits by Risk",
              data: [buckets.Low, buckets.Medium, buckets.High],
            },
          ],
        },
        options: { responsive: true },
      });
    }
  } catch (e) {
    console.error("loadDashboardAdvanced error", e);
  }
}

async function runRiskPrediction() {
  const location = document.getElementById("riskLocation")?.value.trim() || "";
  const historical = parseInt(document.getElementById("riskHistorical")?.value || "0", 10);
  const factorsText = document.getElementById("riskFactors")?.value.trim() || "";

  const environmental_factors = factorsText
    ? factorsText.split("\n").map((x) => x.trim()).filter(Boolean)
    : [];

  const out = document.getElementById("riskResult");
  if (out) out.innerHTML = "جاري التحليل...";

  try {
    const data = await apiFetch("/core/predict-risk", {
      method: "POST",
      body: JSON.stringify({
        location,
        historical_incidents: historical,
        environmental_factors,
      }),
    });

    if (out) {
      out.innerHTML = `
        <div class="success">
          <h4>Risk Score: ${data.risk_score} (${data.risk_level})</h4>
          <ul>${(data.recommendations || []).map((r) => `<li>${r}</li>`).join("")}</ul>
        </div>
      `;
    }
  } catch (e) {
    if (out) out.innerHTML = `<div class="error">خطأ: ${e.message}</div>`;
  }
}

async function loadWorkPermits() {
  const list = document.getElementById("permitsList");
  if (list) list.innerHTML = "<div class='loading'>جاري التحميل...</div>";

  try {
    const permits = await apiFetch("/core/work-permits");
    if (!permits.length) {
      if (list) list.innerHTML = "<div class='loading'>لا توجد تصاريح</div>";
      return;
    }

    if (list) {
      list.innerHTML = permits
        .map(
          (p) => `
      <div class="card">
        <div class="card-body">
          <h4>${p.title}</h4>
          <p>Risk: ${p.risk_level} | Status: ${p.status}</p>
          <small>${p.updated_at || ""}</small>
          <div style="margin-top:.75rem; display:flex; gap:.5rem; flex-wrap:wrap;">
            <button class="btn" onclick="activatePermit('${p.id}')">تفعيل</button>
            <button class="btn" onclick="closePermit('${p.id}')">إغلاق</button>
            <button class="btn" onclick="deletePermit('${p.id}')">حذف</button>
          </div>
        </div>
      </div>
    `
        )
        .join("");
    }
  } catch (e) {
    if (list) list.innerHTML = `<div class="error">خطأ: ${e.message}</div>`;
  }
}

async function createPermit() {
  const title = document.getElementById("permitTitle")?.value.trim() || "";
  const risk_level = document.getElementById("permitRisk")?.value || "Medium";
  const approved_by = document.getElementById("permitApprover")?.value.trim() || null;
  const itemsRaw = document.getElementById("permitChecklist")?.value.trim() || "";
  const checklist_items = itemsRaw ? itemsRaw.split("\n").map((x) => x.trim()).filter(Boolean) : [];

  try {
    await apiFetch("/core/work-permits", {
      method: "POST",
      body: JSON.stringify({ title, risk_level, approved_by, status: "draft", checklist_items }),
    });

    document.getElementById("permitTitle").value = "";
    document.getElementById("permitApprover").value = "";
    document.getElementById("permitChecklist").value = "";

    await loadWorkPermits();
    await loadDashboardAdvanced();
  } catch (e) {
    alert(`خطأ: ${e.message}`);
  }
}

async function activatePermit(id) {
  await apiFetch(`/core/work-permits/${id}`, {
    method: "PUT",
    body: JSON.stringify({ status: "active" }),
  });
  await loadWorkPermits();
  await loadDashboardAdvanced();
}

async function closePermit(id) {
  await apiFetch(`/core/work-permits/${id}`, {
    method: "PUT",
    body: JSON.stringify({ status: "closed" }),
  });
  await loadWorkPermits();
  await loadDashboardAdvanced();
}

async function deletePermit(id) {
  await apiFetch(`/core/work-permits/${id}`, { method: "DELETE" });
  await loadWorkPermits();
  await loadDashboardAdvanced();
}

async function runBehaviorAnalysis() {
  const location = document.getElementById("behaviorLocation")?.value.trim() || "";
  const raw = document.getElementById("behaviorEvents")?.value.trim() || "";

  const events = raw
    ? raw
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line) => {
          const [type, sev] = line.split("|").map((x) => x.trim());
          return { type, severity: parseInt(sev || "1", 10), meta: {} };
        })
    : [];

  const out = document.getElementById("behaviorResult");
  if (out) out.innerHTML = "جاري التحليل...";

  try {
    const data = await apiFetch("/core/behavior-analysis", {
      method: "POST",
      body: JSON.stringify({ location, events }),
    });

    if (out) {
      out.innerHTML = `
        <div class="${data.flagged ? "error" : "success"}">
          <h4>${data.flagged ? "⚠️ تم رصد سلوك خطر" : "✅ الوضع آمن"}</h4>
          <p>Score: ${data.score}</p>
          <ul>${(data.alerts || []).map((a) => `<li>${a}</li>`).join("")}</ul>
          <hr/>
          <ul>${(data.suggestions || []).map((s) => `<li>${s}</li>`).join("")}</ul>
        </div>
      `;
    }
  } catch (e) {
    if (out) out.innerHTML = `<div class="error">خطأ: ${e.message}</div>`;
  }
}

function loadPageData(pageName) {
  switch (pageName) {
    case "dashboard":
      loadDashboardAdvanced();
      break;
    case "riskAnalysis":
      break;
    case "workPermits":
      loadWorkPermits();
      break;
    case "behavior":
      break;
    default:
      break;
  }
}

function bindNavigation() {
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();
      const page = item.dataset.page;
      showPage(page);
    });
  });
}

function init() {
  bindNavigation();
  showPage("dashboard");
}

window.runRiskPrediction = runRiskPrediction;
window.loadWorkPermits = loadWorkPermits;
window.createPermit = createPermit;
window.activatePermit = activatePermit;
window.closePermit = closePermit;
window.deletePermit = deletePermit;
window.runBehaviorAnalysis = runBehaviorAnalysis;

init();
