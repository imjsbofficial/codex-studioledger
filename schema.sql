-- SQLite schema for the Production House Ledger

PRAGMA foreign_keys = ON;

CREATE TABLE projects (
  project_id TEXT PRIMARY KEY,
  project_name TEXT NOT NULL,
  project_by TEXT NOT NULL,
  start_date TEXT NOT NULL,
  end_date TEXT NOT NULL,
  location TEXT NOT NULL,
  project_amount REAL NOT NULL,
  notes TEXT
);

CREATE TABLE project_events (
  event_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  event_date TEXT NOT NULL,
  location TEXT NOT NULL,
  FOREIGN KEY (project_id) REFERENCES projects (project_id)
);

CREATE TABLE team_members (
  team_member_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  role TEXT,
  notes TEXT
);

CREATE TABLE event_assignments (
  assignment_id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  team_member_id TEXT NOT NULL,
  rate REAL NOT NULL,
  FOREIGN KEY (event_id) REFERENCES project_events (event_id),
  FOREIGN KEY (team_member_id) REFERENCES team_members (team_member_id)
);

CREATE TABLE vendor_payments (
  vendor_payment_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  payment_date TEXT NOT NULL,
  amount REAL NOT NULL,
  reference TEXT,
  FOREIGN KEY (project_id) REFERENCES projects (project_id)
);

CREATE TABLE team_member_payments (
  team_payment_id TEXT PRIMARY KEY,
  team_member_id TEXT NOT NULL,
  event_id TEXT NOT NULL,
  payment_date TEXT NOT NULL,
  amount REAL NOT NULL,
  reference TEXT,
  FOREIGN KEY (team_member_id) REFERENCES team_members (team_member_id),
  FOREIGN KEY (event_id) REFERENCES project_events (event_id)
);

CREATE TABLE other_expenses (
  expense_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  event_id TEXT,
  expense_date TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT NOT NULL,
  notes TEXT,
  FOREIGN KEY (project_id) REFERENCES projects (project_id),
  FOREIGN KEY (event_id) REFERENCES project_events (event_id)
);

CREATE VIEW event_cost_summary AS
SELECT
  e.event_id,
  e.project_id,
  e.event_date,
  e.location,
  COALESCE(SUM(a.rate), 0) AS team_cost,
  COALESCE(SUM(x.amount), 0) AS other_expenses
FROM project_events e
LEFT JOIN event_assignments a ON a.event_id = e.event_id
LEFT JOIN other_expenses x ON x.event_id = e.event_id
GROUP BY e.event_id, e.project_id, e.event_date, e.location;

CREATE VIEW project_financials AS
SELECT
  p.project_id,
  p.project_name,
  p.project_by,
  p.start_date,
  p.end_date,
  p.location,
  p.project_amount,
  COALESCE(SUM(v.amount), 0) AS vendor_paid,
  COALESCE(SUM(a.rate), 0) AS team_cost,
  COALESCE(SUM(x.amount), 0) AS other_expenses,
  COALESCE(SUM(a.rate), 0) + COALESCE(SUM(x.amount), 0) AS total_expense,
  COALESCE(SUM(v.amount), 0) - (COALESCE(SUM(a.rate), 0) + COALESCE(SUM(x.amount), 0)) AS profit
FROM projects p
LEFT JOIN vendor_payments v ON v.project_id = p.project_id
LEFT JOIN project_events e ON e.project_id = p.project_id
LEFT JOIN event_assignments a ON a.event_id = e.event_id
LEFT JOIN other_expenses x ON x.project_id = p.project_id
GROUP BY
  p.project_id,
  p.project_name,
  p.project_by,
  p.start_date,
  p.end_date,
  p.location,
  p.project_amount;

CREATE VIEW team_member_balances AS
SELECT
  tm.team_member_id,
  tm.name,
  tm.role,
  COUNT(DISTINCT a.event_id) AS events_assigned,
  COALESCE(SUM(a.rate), 0) AS total_due,
  COALESCE(SUM(tp.amount), 0) AS total_paid,
  COALESCE(SUM(a.rate), 0) - COALESCE(SUM(tp.amount), 0) AS pending_payment
FROM team_members tm
LEFT JOIN event_assignments a ON a.team_member_id = tm.team_member_id
LEFT JOIN team_member_payments tp ON tp.team_member_id = tm.team_member_id
GROUP BY tm.team_member_id, tm.name, tm.role;
