const usage = [
  { project_id: "payments-prod", service: "BigQuery", usage_date: "2026-05-01", cost: 180.5, labels: { env: "prod", owner: "data-platform", business_unit: "payments" } },
  { project_id: "payments-prod", service: "BigQuery", usage_date: "2026-05-02", cost: 190.25, labels: { env: "prod", owner: "data-platform", business_unit: "payments" } },
  { project_id: "payments-prod", service: "BigQuery", usage_date: "2026-05-03", cost: 470.7, labels: { env: "prod", owner: "data-platform", business_unit: "payments" } },
  { project_id: "ml-dev", service: "Compute Engine", usage_date: "2026-05-01", cost: 140.1, labels: { env: "dev", owner: "ml-platform", business_unit: "growth" } },
  { project_id: "ml-dev", service: "Compute Engine", usage_date: "2026-05-02", cost: 145.4, labels: { env: "dev", owner: "ml-platform", business_unit: "growth" } },
  { project_id: "ml-dev", service: "Compute Engine", usage_date: "2026-05-03", cost: 149.8, labels: { env: "dev", owner: "ml-platform", business_unit: "growth" } },
  { project_id: "shared-tools", service: "Cloud Storage", usage_date: "2026-05-01", cost: 52.1, labels: { env: "unknown" } },
  { project_id: "shared-tools", service: "Cloud Storage", usage_date: "2026-05-02", cost: 52.75, labels: { env: "unknown" } },
  { project_id: "shared-tools", service: "Cloud Storage", usage_date: "2026-05-03", cost: 53.2, labels: { env: "unknown" } }
];

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const profile = buildProfile(usage);

function buildProfile(records) {
  const totalCost = round(records.reduce((sum, item) => sum + item.cost, 0));
  const dailyTotals = groupSum(records, "usage_date");
  const forecastMonthlyCost = round(avg(Object.values(dailyTotals)) * 30);
  const portfolio = groupSum(records, "service");
  const findings = [
    ...detectAnomalies(records),
    ...optimizationFindings(records),
    ...governanceFindings(records)
  ];
  const penalty = findings.reduce((sum, finding) => {
    if (finding.severity === "high") return sum + 18;
    if (finding.severity === "medium") return sum + 9;
    return sum;
  }, forecastMonthlyCost > 10000 ? 5 : 0);
  const score = Math.max(0, Math.min(100, 100 - penalty));
  return {
    totalCost,
    forecastMonthlyCost,
    portfolio,
    findings,
    score,
    scoreReason: score >= 85
      ? "Strong usage hygiene with manageable opportunities."
      : score >= 65
        ? "Healthy baseline, but optimization and governance need attention."
        : "Material risks or savings opportunities need immediate action."
  };
}

function groupSum(records, key) {
  return records.reduce((totals, item) => {
    totals[item[key]] = round((totals[item[key]] || 0) + item.cost);
    return totals;
  }, {});
}

function detectAnomalies(records) {
  const byService = records.reduce((groups, item) => {
    groups[item.service] ||= [];
    groups[item.service].push(item);
    return groups;
  }, {});
  return Object.entries(byService).flatMap(([service, items]) => {
    if (items.length < 3) return [];
    const baseline = avg(items.map((item) => item.cost));
    return items
      .filter((item) => baseline > 0 && item.cost >= baseline * 1.6 && item.cost - baseline >= 25)
      .map((item) => ({
        category: "anomaly",
        severity: "high",
        title: `Spend spike in ${service}`,
        description: `${service} cost reached ${money.format(item.cost)} on ${item.usage_date}, above its ${money.format(baseline)} daily baseline.`,
        estimatedMonthlySavings: 0,
        recommendation: "Review recent deployments, traffic changes, and resource scale settings for this service."
      }));
  });
}

function optimizationFindings(records) {
  const grouped = records.reduce((groups, item) => {
    const env = item.labels.env || "unknown";
    const key = `${item.project_id}|${item.service}|${env}`;
    groups[key] ||= { project: item.project_id, service: item.service, env, cost: 0 };
    groups[key].cost += item.cost;
    return groups;
  }, {});
  return Object.values(grouped)
    .filter((item) => ["dev", "test", "unknown"].includes(item.env) && item.cost >= 100)
    .map((item) => ({
      category: "optimization",
      severity: "medium",
      title: `Tune non-production ${item.service} spend`,
      description: `${item.project} spends ${money.format(item.cost)} on ${item.service} in ${item.env}.`,
      estimatedMonthlySavings: round(item.cost * 0.25),
      recommendation: "Apply schedules, right-size resources, and remove idle capacity from non-production workloads."
    }));
}

function governanceFindings(records) {
  const unassignedCost = records
    .filter((item) => !item.labels.owner || !item.labels.business_unit)
    .reduce((sum, item) => sum + item.cost, 0);
  if (!unassignedCost) return [];
  return [{
    category: "governance",
    severity: "medium",
    title: "Unassigned cloud spend",
    description: `${money.format(unassignedCost)} has missing owner or business unit metadata.`,
    estimatedMonthlySavings: 0,
    recommendation: "Enforce labels for owner, business_unit, environment, application, and cost_center."
  }];
}

function answerQuestion(question) {
  const q = question.toLowerCase();
  let focus = "overall cloud usage";
  let findings = profile.findings.slice(0, 5);
  if (["save", "saving", "optimize", "recommend"].some((term) => q.includes(term))) {
    focus = "savings and optimization";
    findings = profile.findings.filter((finding) => finding.category === "optimization");
  } else if (["anomaly", "anomalies", "spike", "increase", "why"].some((term) => q.includes(term))) {
    focus = "anomalies";
    findings = profile.findings.filter((finding) => finding.category === "anomaly");
  } else if (["governance", "label", "owner", "chargeback"].some((term) => q.includes(term))) {
    focus = "governance";
    findings = profile.findings.filter((finding) => finding.category === "governance");
  }
  const savings = round(findings.reduce((sum, finding) => sum + finding.estimatedMonthlySavings, 0));
  const top = findings[0];
  if (!top) return `CloudScore is ${profile.score}. No matching ${focus} findings were detected.`;
  const savingsText = savings ? ` Estimated monthly savings: ${money.format(savings)}.` : "";
  return `CloudScore is ${profile.score}. Top ${focus} issue: ${top.title}. ${top.description}${savingsText}`;
}

function render() {
  const savings = round(profile.findings.reduce((sum, finding) => sum + finding.estimatedMonthlySavings, 0));
  document.querySelector("#score").textContent = profile.score;
  document.querySelector("#score-large").textContent = profile.score;
  document.querySelector("#score-reason").textContent = profile.scoreReason;
  document.querySelector("#total-cost").textContent = money.format(profile.totalCost);
  document.querySelector("#forecast").textContent = money.format(profile.forecastMonthlyCost);
  document.querySelector("#savings").textContent = money.format(savings);
  document.querySelector("#finding-count").textContent = profile.findings.length;
  document.querySelector("#score-arc").style.strokeDashoffset = String(302 - (302 * profile.score) / 100);
  renderPortfolio();
  renderFindings();
  document.querySelector("#answer").textContent = answerQuestion(document.querySelector("#question").value);
}

function renderPortfolio() {
  const max = Math.max(...Object.values(profile.portfolio));
  document.querySelector("#portfolio").innerHTML = Object.entries(profile.portfolio)
    .sort((a, b) => b[1] - a[1])
    .map(([service, cost]) => `
      <div class="bar-row">
        <strong>${service}</strong>
        <div class="bar-track"><div class="bar-fill" style="width: ${(cost / max) * 100}%"></div></div>
        <span>${money.format(cost)}</span>
      </div>
    `).join("");
}

function renderFindings() {
  const filter = document.querySelector("#filter").value;
  const findings = filter === "all"
    ? profile.findings
    : profile.findings.filter((finding) => finding.category === filter);
  document.querySelector("#findings").innerHTML = findings.map((finding) => `
    <article class="finding">
      <div class="finding-head">
        <h3>${finding.title}</h3>
        <span class="tag ${finding.severity}">${finding.severity}</span>
      </div>
      <p>${finding.description}</p>
      <p class="recommendation"><strong>Action:</strong> ${finding.recommendation}</p>
    </article>
  `).join("");
}

function avg(values) {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function round(value) {
  return Math.round(value * 100) / 100;
}

document.querySelector("#ask-form").addEventListener("submit", (event) => {
  event.preventDefault();
  document.querySelector("#answer").textContent = answerQuestion(document.querySelector("#question").value);
});
document.querySelector("#filter").addEventListener("change", renderFindings);
render();
