// ── Telco Churn Executive Web Application ─────────────────────────────────

const API_BASE = window.location.origin;

// Predefined Customer Personas for One-Click Demos
const PERSONAS = {
  highRisk: {
    name: "High-Risk New Account",
    data: {
      gender: "Female",
      SeniorCitizen: 0,
      Partner: "No",
      Dependents: "No",
      tenure: 1,
      PhoneService: "Yes",
      MultipleLines: "No",
      InternetService: "Fiber optic",
      OnlineSecurity: "No",
      OnlineBackup: "No",
      DeviceProtection: "No",
      TechSupport: "No",
      StreamingTV: "Yes",
      StreamingMovies: "Yes",
      Contract: "Month-to-month",
      PaperlessBilling: "Yes",
      PaymentMethod: "Electronic check",
      MonthlyCharges: 95.85,
      TotalCharges: 95.85
    }
  },
  loyalAccount: {
    name: "Loyal Long-Term Account",
    data: {
      gender: "Male",
      SeniorCitizen: 0,
      Partner: "Yes",
      Dependents: "Yes",
      tenure: 62,
      PhoneService: "Yes",
      MultipleLines: "Yes",
      InternetService: "DSL",
      OnlineSecurity: "Yes",
      OnlineBackup: "Yes",
      DeviceProtection: "Yes",
      TechSupport: "Yes",
      StreamingTV: "Yes",
      StreamingMovies: "Yes",
      Contract: "Two year",
      PaperlessBilling: "No",
      PaymentMethod: "Bank transfer (automatic)",
      MonthlyCharges: 75.50,
      TotalCharges: 4681.00
    }
  },
  budgetAtRisk: {
    name: "Budget Customer (At Risk)",
    data: {
      gender: "Male",
      SeniorCitizen: 1,
      Partner: "No",
      Dependents: "No",
      tenure: 4,
      PhoneService: "Yes",
      MultipleLines: "No",
      InternetService: "DSL",
      OnlineSecurity: "No",
      OnlineBackup: "No",
      DeviceProtection: "No",
      TechSupport: "No",
      StreamingTV: "No",
      StreamingMovies: "No",
      Contract: "Month-to-month",
      PaperlessBilling: "Yes",
      PaymentMethod: "Electronic check",
      MonthlyCharges: 45.30,
      TotalCharges: 181.20
    }
  },
  standardFamily: {
    name: "Standard Family Plan",
    data: {
      gender: "Female",
      SeniorCitizen: 0,
      Partner: "Yes",
      Dependents: "Yes",
      tenure: 36,
      PhoneService: "Yes",
      MultipleLines: "Yes",
      InternetService: "Fiber optic",
      OnlineSecurity: "Yes",
      OnlineBackup: "Yes",
      DeviceProtection: "Yes",
      TechSupport: "No",
      StreamingTV: "Yes",
      StreamingMovies: "Yes",
      Contract: "One year",
      PaperlessBilling: "Yes",
      PaymentMethod: "Credit card (automatic)",
      MonthlyCharges: 102.40,
      TotalCharges: 3686.40
    }
  }
};

// ── Application Initialization ────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initSimulator();
  initBatchStudio();
  initModelViewer();
  fetchSystemInfo();
});

// ── Navigation Tabs ───────────────────────────────────────────────────────
function initNavigation() {
  const navBtns = document.querySelectorAll(".nav-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      navBtns.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetElement = document.getElementById(targetTab);
      if (targetElement) targetElement.classList.add("active");
    });
  });
}

// ── Fetch Global Model Info ───────────────────────────────────────────────
async function fetchSystemInfo() {
  try {
    const res = await fetch(`${API_BASE}/model/info`);
    if (res.ok) {
      const data = await res.json();
      const rawName = data.model_name || "LogisticRegression";
      const formattedName = rawName.replace(/([a-z])([A-Z])/g, "$1 $2").trim();
      document.getElementById("kpi-champion-model").textContent = formattedName;
      if (data.test_metrics) {
        document.getElementById("kpi-roc-auc").textContent = (data.test_metrics.roc_auc * 100).toFixed(1) + "%";
        document.getElementById("kpi-accuracy").textContent = (data.test_metrics.accuracy * 100).toFixed(1) + "%";
      }
      document.getElementById("sys-status-text").textContent = "API & Model Online";
    }
  } catch (err) {
    console.warn("Could not fetch model info:", err);
    document.getElementById("sys-status-text").textContent = "Running (Offline Mock)";
  }
}

// ── Simulator & What-If Studio ────────────────────────────────────────────
function initSimulator() {
  const form = document.getElementById("simulator-form");
  const pills = document.querySelectorAll(".persona-pill");

  // Load default High-Risk persona
  loadPersona("highRisk");

  // Persona buttons click
  pills.forEach(pill => {
    pill.addEventListener("click", () => {
      pills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      const personaKey = pill.getAttribute("data-persona");
      loadPersona(personaKey);
      runSinglePrediction();
    });
  });

  // Re-run on form changes
  form.addEventListener("change", () => {
    runSinglePrediction();
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    runSinglePrediction();
  });

  // Initial calculation
  runSinglePrediction();
}

function loadPersona(key) {
  const persona = PERSONAS[key];
  if (!persona) return;

  const data = persona.data;
  Object.keys(data).forEach(field => {
    const el = document.getElementById(`sim-${field}`);
    if (el) el.value = data[field];
  });
}

function getFormData() {
  return {
    gender: document.getElementById("sim-gender").value,
    SeniorCitizen: parseInt(document.getElementById("sim-SeniorCitizen").value, 10),
    Partner: document.getElementById("sim-Partner").value,
    Dependents: document.getElementById("sim-Dependents").value,
    tenure: parseInt(document.getElementById("sim-tenure").value, 10) || 0,
    PhoneService: document.getElementById("sim-PhoneService").value,
    MultipleLines: document.getElementById("sim-MultipleLines").value,
    InternetService: document.getElementById("sim-InternetService").value,
    OnlineSecurity: document.getElementById("sim-OnlineSecurity").value,
    OnlineBackup: document.getElementById("sim-OnlineBackup").value,
    DeviceProtection: document.getElementById("sim-DeviceProtection").value,
    TechSupport: document.getElementById("sim-TechSupport").value,
    StreamingTV: document.getElementById("sim-StreamingTV").value,
    StreamingMovies: document.getElementById("sim-StreamingMovies").value,
    Contract: document.getElementById("sim-Contract").value,
    PaperlessBilling: document.getElementById("sim-PaperlessBilling").value,
    PaymentMethod: document.getElementById("sim-PaymentMethod").value,
    MonthlyCharges: parseFloat(document.getElementById("sim-MonthlyCharges").value) || 0,
    TotalCharges: parseFloat(document.getElementById("sim-TotalCharges").value) || 0,
  };
}

async function runSinglePrediction() {
  const payload = getFormData();

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error("Prediction request failed");
    const result = await response.json();
    updateGauge(result.probability);
    generateRecommendations(payload, result.probability);
  } catch (error) {
    console.error("Predict error:", error);
  }
}

// ── Animated Gauge Meter ──────────────────────────────────────────────────
function updateGauge(probability) {
  const percentage = Math.round(probability * 100);
  const percentEl = document.getElementById("gauge-percent");
  const badgeEl = document.getElementById("risk-tier-badge");
  const gaugeBar = document.getElementById("gauge-bar");

  // Animate text
  percentEl.textContent = `${percentage}%`;

  // SVG perimeter is 2 * PI * 80 ≈ 502.65
  const circumference = 502.65;
  const offset = circumference - (probability * circumference);
  gaugeBar.style.strokeDashoffset = offset;

  // Color & Badge determination
  if (percentage < 30) {
    gaugeBar.style.stroke = "var(--accent-emerald)";
    badgeEl.className = "risk-badge low";
    badgeEl.textContent = "Low Risk (Safe)";
  } else if (percentage < 60) {
    gaugeBar.style.stroke = "var(--accent-amber)";
    badgeEl.className = "risk-badge medium";
    badgeEl.textContent = "Moderate Risk (Monitor)";
  } else {
    gaugeBar.style.stroke = "var(--accent-rose)";
    badgeEl.className = "risk-badge high";
    badgeEl.textContent = "High Risk (Intervention Needed)";
  }
}

// ── Smart Retention Engine ────────────────────────────────────────────────
function generateRecommendations(data, prob) {
  const list = document.getElementById("recommendation-list");
  list.innerHTML = "";

  const recommendations = [];

  if (prob < 0.3) {
    recommendations.push("Account is healthy and stable. Consider presenting upgrade cross-sell bundles (e.g., Streaming or Device Protection).");
    recommendations.push("Customer exhibits high loyalty patterns. No immediate retention discount required.");
  } else {
    if (data.Contract === "Month-to-month") {
      recommendations.push("<strong>Migrate Contract:</strong> Customer is on month-to-month billing. Offer a 1-year or 2-year plan discount (typically reduces churn risk by ~38%).");
    }
    if (data.PaymentMethod === "Electronic check") {
      recommendations.push("<strong>Payment Method:</strong> Electronic check users show 40% higher churn. Incentivize automated credit card or direct bank debit with a $5 bill credit.");
    }
    if (data.InternetService === "Fiber optic" && (data.OnlineSecurity === "No" || data.TechSupport === "No")) {
      recommendations.push("<strong>Service Health:</strong> High fiber charges without Tech Support or Security. Offer a complimentary 60-day Tech Support & Security pack to improve satisfaction.");
    }
    if (data.tenure <= 6) {
      recommendations.push("<strong>Onboarding Window:</strong> Customer is in their first 6 months (highest churn hazard). Assign account for customer success welcome call.");
    }
  }

  if (recommendations.length === 0) {
    recommendations.push("Account metrics are balanced. Standard engagement guidelines apply.");
  }

  recommendations.forEach(text => {
    const li = document.createElement("li");
    li.className = "recom-item";
    li.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="2" stroke-linecap="round"/></svg>
      <span>${text}</span>
    `;
    list.appendChild(li);
  });
}

// ── Batch Analysis Studio ─────────────────────────────────────────────────
const SAMPLE_COHORT = [
  { ...PERSONAS.highRisk.data, customerID: "CUST-901" },
  { ...PERSONAS.loyalAccount.data, customerID: "CUST-902" },
  { ...PERSONAS.budgetAtRisk.data, customerID: "CUST-903" },
  { ...PERSONAS.standardFamily.data, customerID: "CUST-904" },
  { ...PERSONAS.highRisk.data, customerID: "CUST-905", tenure: 2, MonthlyCharges: 89.20, TotalCharges: 178.40 },
  { ...PERSONAS.loyalAccount.data, customerID: "CUST-906", MonthlyCharges: 60.10, TotalCharges: 3600.00 },
  { ...PERSONAS.budgetAtRisk.data, customerID: "CUST-907", tenure: 8, MonthlyCharges: 42.00, TotalCharges: 336.00 },
  { ...PERSONAS.standardFamily.data, customerID: "CUST-908", tenure: 48, MonthlyCharges: 110.00, TotalCharges: 5280.00 }
];

function initBatchStudio() {
  const loadBtn = document.getElementById("load-sample-batch-btn");
  if (loadBtn) {
    loadBtn.addEventListener("click", () => {
      runBatchAnalysis(SAMPLE_COHORT);
    });
  }
}

async function runBatchAnalysis(customers) {
  const tbody = document.getElementById("batch-table-body");
  tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 24px; color: var(--text-muted);">Scoring ${customers.length} accounts through pipeline...</td></tr>`;

  try {
    const response = await fetch(`${API_BASE}/predict/batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(customers)
    });

    if (!response.ok) throw new Error("Batch prediction failed");
    const result = await response.json();

    tbody.innerHTML = "";
    let highRiskCount = 0;

    result.predictions.forEach((pred, idx) => {
      const cust = customers[idx];
      const probPercent = Math.round(pred.probability * 100);
      const isHigh = pred.prediction === 1;
      if (isHigh) highRiskCount++;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-family: monospace; font-weight: 600;">${cust.customerID || `CUST-${idx + 101}`}</td>
        <td>${cust.tenure} mos</td>
        <td>${cust.Contract}</td>
        <td>${cust.InternetService}</td>
        <td>$${cust.MonthlyCharges.toFixed(2)}</td>
        <td style="font-weight: 700; color: ${probPercent > 50 ? 'var(--accent-rose)' : 'var(--accent-emerald)'};">
          ${probPercent}%
        </td>
        <td>
          <span class="risk-badge ${probPercent < 30 ? 'low' : probPercent < 60 ? 'medium' : 'high'}" style="padding: 4px 10px; font-size: 0.75rem;">
            ${pred.label}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Update batch stats
    document.getElementById("batch-total-count").textContent = customers.length;
    document.getElementById("batch-high-risk-count").textContent = highRiskCount;
    document.getElementById("batch-safe-count").textContent = customers.length - highRiskCount;

  } catch (error) {
    console.error("Batch error:", error);
    tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--accent-rose);">Batch error: ${error.message}</td></tr>`;
  }
}

// ── Model Explainability & Artifacts ──────────────────────────────────────
function initModelViewer() {
  const modelBtns = document.querySelectorAll(".model-tab-btn");
  const cmImg = document.getElementById("artifact-cm-img");
  const fiImg = document.getElementById("artifact-fi-img");

  modelBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      modelBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const modelName = btn.getAttribute("data-model");

      if (cmImg) cmImg.src = `/artifacts/cm_${modelName}.png`;
      if (fiImg) fiImg.src = `/artifacts/fi_${modelName}.png`;
    });
  });
}
