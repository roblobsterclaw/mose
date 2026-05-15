PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS investors (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  fund TEXT,
  tier INTEGER NOT NULL,
  source_type TEXT NOT NULL DEFAULT '13F',
  cik TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS filings (
  id INTEGER PRIMARY KEY,
  investor_id INTEGER NOT NULL REFERENCES investors(id) ON DELETE CASCADE,
  source TEXT NOT NULL,
  accession TEXT,
  filing_date TEXT,
  report_period TEXT,
  total_value REAL,
  num_holdings INTEGER,
  raw_payload TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(investor_id, source, accession)
);

CREATE TABLE IF NOT EXISTS securities (
  id INTEGER PRIMARY KEY,
  ticker TEXT NOT NULL UNIQUE,
  company TEXT,
  cusip TEXT,
  asset_type TEXT NOT NULL DEFAULT 'equity',
  display_name TEXT,
  exchange TEXT,
  sector TEXT,
  industry TEXT,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS market_symbols (
  id INTEGER PRIMARY KEY,
  security_id INTEGER REFERENCES securities(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  symbol_type TEXT NOT NULL DEFAULT 'equity',
  provider_symbol TEXT,
  topbar INTEGER NOT NULL DEFAULT 0,
  chart_enabled INTEGER NOT NULL DEFAULT 1,
  active INTEGER NOT NULL DEFAULT 1,
  sort_order INTEGER NOT NULL DEFAULT 100,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS holdings (
  id INTEGER PRIMARY KEY,
  filing_id INTEGER NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
  investor_id INTEGER NOT NULL REFERENCES investors(id) ON DELETE CASCADE,
  security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  shares REAL,
  market_value REAL,
  pct_of_portfolio REAL,
  rank_in_portfolio INTEGER,
  is_top5 INTEGER NOT NULL DEFAULT 0,
  source TEXT NOT NULL DEFAULT 'convergence-master.json',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(filing_id, security_id)
);

CREATE TABLE IF NOT EXISTS convergence_rankings (
  id INTEGER PRIMARY KEY,
  security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  generated_at TEXT NOT NULL,
  convergence_score REAL NOT NULL DEFAULT 0,
  total_investor_count INTEGER NOT NULL DEFAULT 0,
  tier1_count INTEGER NOT NULL DEFAULT 0,
  tier2_count INTEGER NOT NULL DEFAULT 0,
  tier3_count INTEGER NOT NULL DEFAULT 0,
  total_conviction_pct REAL NOT NULL DEFAULT 0,
  total_value_held REAL NOT NULL DEFAULT 0,
  top5_bonus_count INTEGER NOT NULL DEFAULT 0,
  raw_investors TEXT NOT NULL DEFAULT '[]',
  UNIQUE(security_id, generated_at)
);

CREATE TABLE IF NOT EXISTS price_snapshots (
  id INTEGER PRIMARY KEY,
  security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  price REAL NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USD',
  change_pct REAL,
  volume REAL,
  market_status TEXT,
  source TEXT NOT NULL,
  fetched_at TEXT NOT NULL,
  raw_payload TEXT,
  UNIQUE(security_id, source, fetched_at)
);

CREATE TABLE IF NOT EXISTS price_history (
  id INTEGER PRIMARY KEY,
  security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  price_date TEXT NOT NULL,
  open REAL,
  high REAL,
  low REAL,
  close REAL NOT NULL,
  volume REAL,
  source TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(security_id, price_date, source)
);

CREATE TABLE IF NOT EXISTS symbol_metrics (
  id INTEGER PRIMARY KEY,
  security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  metric_date TEXT NOT NULL,
  market_cap REAL,
  pe_ratio REAL,
  forward_pe REAL,
  dividend_yield REAL,
  beta REAL,
  eps_ttm REAL,
  revenue_growth REAL,
  week_52_high REAL,
  week_52_low REAL,
  source TEXT NOT NULL,
  raw_payload TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(security_id, metric_date, source)
);

CREATE TABLE IF NOT EXISTS symbol_profiles (
  id INTEGER PRIMARY KEY,
  security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  description TEXT,
  website TEXT,
  logo_url TEXT,
  country TEXT,
  exchange TEXT,
  source TEXT NOT NULL,
  raw_payload TEXT,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(security_id, source)
);

CREATE TABLE IF NOT EXISTS portfolio_accounts (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  brokerage TEXT,
  account_type TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS portfolio_lots (
  id INTEGER PRIMARY KEY,
  account_id INTEGER REFERENCES portfolio_accounts(id) ON DELETE SET NULL,
  security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  shares REAL NOT NULL,
  cost_basis_per_share REAL,
  opened_at TEXT,
  source TEXT NOT NULL DEFAULT 'manual',
  broker_lot_id TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS signals (
  id INTEGER PRIMARY KEY,
  security_id INTEGER REFERENCES securities(id) ON DELETE SET NULL,
  signal_type TEXT NOT NULL,
  confidence TEXT NOT NULL DEFAULT 'unverified',
  severity TEXT NOT NULL DEFAULT 'info',
  summary TEXT NOT NULL,
  source TEXT NOT NULL,
  observed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  raw_payload TEXT
);

CREATE TABLE IF NOT EXISTS research_items (
  id INTEGER PRIMARY KEY,
  security_id INTEGER NOT NULL REFERENCES securities(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'needs',
  priority TEXT NOT NULL DEFAULT 'None',
  trigger_reason TEXT,
  source TEXT NOT NULL DEFAULT 'manual',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(security_id)
);

CREATE TABLE IF NOT EXISTS research_reports (
  id INTEGER PRIMARY KEY,
  research_item_id INTEGER NOT NULL REFERENCES research_items(id) ON DELETE CASCADE,
  thesis TEXT,
  risks TEXT,
  valuation_notes TEXT,
  portfolio_fit TEXT,
  source_notes TEXT,
  confidence TEXT NOT NULL DEFAULT 'draft',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS source_events (
  id INTEGER PRIMARY KEY,
  source TEXT NOT NULL,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL,
  summary TEXT,
  payload TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS export_runs (
  id INTEGER PRIMARY KEY,
  export_path TEXT NOT NULL,
  generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  investor_count INTEGER NOT NULL DEFAULT 0,
  security_count INTEGER NOT NULL DEFAULT 0,
  ranking_count INTEGER NOT NULL DEFAULT 0,
  notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_holdings_investor ON holdings(investor_id);
CREATE INDEX IF NOT EXISTS idx_holdings_security ON holdings(security_id);
CREATE INDEX IF NOT EXISTS idx_filings_investor_date ON filings(investor_id, filing_date);
CREATE INDEX IF NOT EXISTS idx_rankings_generated ON convergence_rankings(generated_at);
CREATE INDEX IF NOT EXISTS idx_prices_security_fetched ON price_snapshots(security_id, fetched_at);
CREATE INDEX IF NOT EXISTS idx_market_symbols_active ON market_symbols(active, topbar, sort_order);
CREATE INDEX IF NOT EXISTS idx_price_history_security_date ON price_history(security_id, price_date);
CREATE INDEX IF NOT EXISTS idx_symbol_metrics_security_date ON symbol_metrics(security_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_research_items_status ON research_items(status, priority);

INSERT OR IGNORE INTO schema_migrations (version) VALUES ('001_initial_sqlite_truth_store');
