const models = [
  { provider: "Google", model: "Gemini Flash", workload: "Simple tasks", cost: 0.00038, quality: 86, latency: 930, savings: 96 },
  { provider: "AWS Bedrock", model: "Claude Haiku", workload: "Extraction + RAG", cost: 0.0015, quality: 84, latency: 950, savings: 88 },
  { provider: "Anthropic", model: "Claude Sonnet", workload: "Moderate reasoning", cost: 0.018, quality: 95, latency: 1950, savings: 28 },
  { provider: "OpenAI", model: "GPT-4o", workload: "Complex reasoning", cost: 0.02, quality: 96, latency: 2100, savings: 0 },
  { provider: "Groq", model: "Llama 70B", workload: "Low-latency chat", cost: 0.0011, quality: 88, latency: 520, savings: 91 }
];

const routingRows = [
  { task: "Classification", route: "Google / Gemini Flash", reason: "Low complexity, high volume, budget guardrail active", savings: "$1.2M" },
  { task: "RAG Search", route: "AWS Bedrock / Claude Haiku", reason: "Compliant provider, strong extraction quality", savings: "$620K" },
  { task: "Code Generation", route: "OpenAI / GPT-4o", reason: "Quality floor requires frontier reasoning", savings: "$0" },
  { task: "Summarization", route: "Groq / Llama 70B", reason: "Latency-sensitive and cache-friendly", savings: "$410K" }
];

const policies = [
  ["Premium model restriction", "Interns and contractors route away from frontier models unless approved."],
  ["Token budget enforcement", "Requests above 120k tokens are compressed and pruned before routing."],
  ["Provider compliance", "HIPAA workloads require OpenAI, Anthropic, Azure OpenAI, or Bedrock."],
  ["Runaway protection", "Near-limit teams are downgraded, throttled, and alerted automatically."]
];

const cacheLayers = [
  ["L1", "Exact Match", "11% hit rate"],
  ["L2", "Semantic Similarity", "18% hit rate"],
  ["L3", "Summary Cache", "4% hit rate"],
  ["L4", "Conversation Context", "Preview"]
];

const forecast = [
  ["Week 1", 62, 18],
  ["Week 2", 72, 29],
  ["Week 3", 88, 41],
  ["Week 4", 106, 52],
  ["Week 5", 124, 61]
];

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 4 });

function estimateTokens(text) {
  return Math.max(1, Math.ceil(text.trim().split(/\s+/).length * 1.08));
}

function routeRequest(prompt, task) {
  const promptTokens = estimateTokens(prompt);
  const simpleTasks = ["classification", "extraction", "summarization"];
  let selected = models[2];
  if (simpleTasks.includes(task)) selected = models[0];
  if (task === "code_generation" || task === "complex_reasoning") selected = models[3];
  if (task === "analytics" || task === "structured_output") selected = models[2];
  const outputTokens = Math.min(1024, Math.max(48, Math.round(promptTokens * 0.55)));
  const baselineCost = (promptTokens / 1000) * 0.005 + (outputTokens / 1000) * 0.015;
  const selectedCost = selected.cost * (promptTokens + outputTokens);
  const savings = Math.max(0, baselineCost - selectedCost);
  const cacheHit = prompt.toLowerCase().includes("may llm spend");
  return { selected, promptTokens, outputTokens, baselineCost, selectedCost: cacheHit ? 0 : selectedCost, savings, cacheHit };
}

function renderRouting() {
  document.querySelector("#routing-table").innerHTML = `
    <div class="table-row table-head"><span>Task</span><span>Selected route</span><span>Decision reason</span><span>Savings</span></div>
    ${routingRows.map((row) => `
      <div class="table-row">
        <strong>${row.task}</strong>
        <span>${row.route}</span>
        <span>${row.reason}</span>
        <strong>${row.savings}</strong>
      </div>
    `).join("")}`;
}

function renderCache() {
  document.querySelector("#cache-layers").innerHTML = cacheLayers.map(([level, name, stat]) => `
    <div class="stack-item">
      <span>${level}</span>
      <strong>${name}</strong>
      <small>${stat}</small>
    </div>
  `).join("");
}

function renderBudget() {
  document.querySelector("#budget-fill").style.width = "68%";
  document.querySelector("#budget-status").innerHTML = [
    ["Organization", "$342K / $500K", "healthy"],
    ["Customer AI", "$91K / $100K", "warning"],
    ["Internal Agents", "$44K / $80K", "healthy"]
  ].map(([name, spend, status]) => `<div><span>${name}</span><strong>${spend}</strong><em class="${status}">${status}</em></div>`).join("");
}

function renderAdvisor() {
  const maxCost = Math.max(...models.map((model) => model.cost));
  document.querySelector("#advisor-chart").innerHTML = models.map((model) => `
    <div class="bubble" style="left:${(model.cost / maxCost) * 82 + 6}%; bottom:${model.quality - 68}%">
      <span>${model.provider}</span>
    </div>
  `).join("") + `<span class="axis x">Monthly cost →</span><span class="axis y">Quality →</span>`;
}

function renderMigration() {
  document.querySelector("#migration-card").innerHTML = `
    <strong>GPT-4o → Gemini Flash</strong>
    <div><span>Cost reduction</span><b>96.1%</b></div>
    <div><span>Latency change</span><b>-1.17s</b></div>
    <div><span>Quality risk</span><b>0.10</b></div>
    <div><span>Confidence</span><b>82%</b></div>
  `;
}

function renderProviders() {
  document.querySelector("#provider-health").innerHTML = models.map((model) => `
    <div class="stack-item">
      <span>${model.provider}</span>
      <strong>${model.latency}ms p95</strong>
      <small>${model.quality}% quality</small>
    </div>
  `).join("");
}

function renderPolicies() {
  document.querySelector("#policy-list").innerHTML = policies.map(([title, body]) => `
    <article>
      <strong>${title}</strong>
      <p>${body}</p>
    </article>
  `).join("");
}

function renderForecast() {
  const max = Math.max(...forecast.map((row) => row[1]));
  document.querySelector("#forecast-chart").innerHTML = forecast.map(([label, spend, savings]) => `
    <div class="forecast-col">
      <div class="bars-pair">
        <span class="spend" style="height:${(spend / max) * 100}%"></span>
        <span class="save" style="height:${(savings / max) * 100}%"></span>
      </div>
      <small>${label}</small>
    </div>
  `).join("");
}

function renderGatewayResult(event) {
  event.preventDefault();
  const prompt = document.querySelector("#prompt").value;
  const task = document.querySelector("#task").value;
  const result = routeRequest(prompt, task);
  document.querySelector("#gateway-result").innerHTML = `
    <div><span>Selected provider</span><strong>${result.selected.provider} / ${result.selected.model}</strong></div>
    <div><span>Tokens</span><strong>${result.promptTokens + result.outputTokens}</strong></div>
    <div><span>Estimated request cost</span><strong>${money.format(result.selectedCost)}</strong></div>
    <div><span>Cache</span><strong>${result.cacheHit ? "L2 semantic hit" : "Write scheduled"}</strong></div>
    <p>${result.selected.workload} route selected with ${result.selected.quality}% quality score and ${result.selected.latency}ms p95 latency.</p>
  `;
}

function init() {
  renderRouting();
  renderCache();
  renderBudget();
  renderAdvisor();
  renderMigration();
  renderProviders();
  renderPolicies();
  renderForecast();
  document.querySelector("#gateway-form").addEventListener("submit", renderGatewayResult);
  document.querySelector("#theme-toggle").addEventListener("click", () => {
    document.documentElement.toggleAttribute("data-dark");
  });
  document.querySelector("#gateway-form").dispatchEvent(new Event("submit", { cancelable: true }));
}

init();
