CREATE TABLE organizations (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  plan TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE teams (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  monthly_budget_usd NUMERIC(14, 4) NOT NULL DEFAULT 0
);

CREATE TABLE users (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  team_id UUID REFERENCES teams(id),
  email TEXT NOT NULL,
  role TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE projects (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  team_id UUID REFERENCES teams(id),
  name TEXT NOT NULL,
  environment TEXT NOT NULL
);

CREATE TABLE providers (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  health_score NUMERIC(5, 4) NOT NULL,
  compliance_tags TEXT[] NOT NULL DEFAULT '{}'
);

CREATE TABLE models (
  id UUID PRIMARY KEY,
  provider_id UUID NOT NULL REFERENCES providers(id),
  name TEXT NOT NULL,
  input_cost_per_1k NUMERIC(12, 8) NOT NULL,
  output_cost_per_1k NUMERIC(12, 8) NOT NULL,
  quality_score NUMERIC(5, 4) NOT NULL,
  context_window INTEGER NOT NULL
);

CREATE TABLE requests (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  team_id UUID REFERENCES teams(id),
  project_id UUID REFERENCES projects(id),
  user_id UUID REFERENCES users(id),
  task_category TEXT NOT NULL,
  prompt_hash TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE responses (
  id UUID PRIMARY KEY,
  request_id UUID NOT NULL REFERENCES requests(id),
  provider_id UUID NOT NULL REFERENCES providers(id),
  model_id UUID NOT NULL REFERENCES models(id),
  latency_ms INTEGER NOT NULL,
  quality_score NUMERIC(5, 4) NOT NULL,
  hallucination_score NUMERIC(5, 4) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE token_usage (
  id UUID PRIMARY KEY,
  request_id UUID NOT NULL REFERENCES requests(id),
  prompt_tokens INTEGER NOT NULL,
  completion_tokens INTEGER NOT NULL,
  total_tokens INTEGER NOT NULL,
  cost_usd NUMERIC(14, 8) NOT NULL
);

CREATE TABLE routing_decisions (
  id UUID PRIMARY KEY,
  request_id UUID NOT NULL REFERENCES requests(id),
  selected_provider TEXT NOT NULL,
  selected_model TEXT NOT NULL,
  estimated_cost_usd NUMERIC(14, 8) NOT NULL,
  estimated_latency_ms INTEGER NOT NULL,
  confidence_score NUMERIC(5, 4) NOT NULL,
  optimization_reason TEXT NOT NULL
);

CREATE TABLE cache_entries (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  prompt_hash TEXT NOT NULL,
  response_hash TEXT NOT NULL,
  cache_layer TEXT NOT NULL,
  trust_score NUMERIC(5, 4) NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE optimization_actions (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  request_id UUID REFERENCES requests(id),
  action_type TEXT NOT NULL,
  status TEXT NOT NULL,
  savings_usd NUMERIC(14, 8) NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE budget_policies (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  scope_type TEXT NOT NULL,
  scope_id UUID,
  monthly_budget_usd NUMERIC(14, 4) NOT NULL,
  enforcement_mode TEXT NOT NULL
);

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  actor_id UUID,
  action TEXT NOT NULL,
  target TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
