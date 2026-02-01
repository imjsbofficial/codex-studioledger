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
WITH assignment_totals AS (
  SELECT event_id, SUM(rate) AS team_cost
  FROM event_assignments
  GROUP BY event_id
),
expense_totals AS (
  SELECT event_id, SUM(amount) AS other_expenses
  FROM other_expenses
  GROUP BY event_id
)
SELECT
  e.event_id,
  e.project_id,
  e.event_date,
  e.location,
  COALESCE(a.team_cost, 0) AS team_cost,
  COALESCE(x.other_expenses, 0) AS other_expenses
FROM project_events e
LEFT JOIN assignment_totals a ON a.event_id = e.event_id
LEFT JOIN expense_totals x ON x.event_id = e.event_id;

CREATE VIEW project_financials AS
WITH vendor_totals AS (
  SELECT project_id, SUM(amount) AS vendor_paid
  FROM vendor_payments
  GROUP BY project_id
),
team_totals AS (
  SELECT e.project_id, SUM(a.rate) AS team_cost
  FROM project_events e
  JOIN event_assignments a ON a.event_id = e.event_id
  GROUP BY e.project_id
),
expense_totals AS (
  SELECT project_id, SUM(amount) AS other_expenses
  FROM other_expenses
  GROUP BY project_id
)
SELECT
  p.project_id,
  p.project_name,
  p.project_by,
  p.start_date,
  p.end_date,
  p.location,
  p.project_amount,
  COALESCE(v.vendor_paid, 0) AS vendor_paid,
  COALESCE(t.team_cost, 0) AS team_cost,
  COALESCE(x.other_expenses, 0) AS other_expenses,
  COALESCE(t.team_cost, 0) + COALESCE(x.other_expenses, 0) AS total_expense,
  COALESCE(v.vendor_paid, 0) - (COALESCE(t.team_cost, 0) + COALESCE(x.other_expenses, 0)) AS profit
FROM projects p
LEFT JOIN vendor_totals v ON v.project_id = p.project_id
LEFT JOIN team_totals t ON t.project_id = p.project_id
LEFT JOIN expense_totals x ON x.project_id = p.project_id;

CREATE VIEW team_member_balances AS
WITH assignment_totals AS (
  SELECT team_member_id, COUNT(DISTINCT event_id) AS events_assigned, SUM(rate) AS total_due
  FROM event_assignments
  GROUP BY team_member_id
),
payment_totals AS (
  SELECT team_member_id, SUM(amount) AS total_paid
  FROM team_member_payments
  GROUP BY team_member_id
)
SELECT
  tm.team_member_id,
  tm.name,
  tm.role,
  COALESCE(a.events_assigned, 0) AS events_assigned,
  COALESCE(a.total_due, 0) AS total_due,
  COALESCE(p.total_paid, 0) AS total_paid,
  COALESCE(a.total_due, 0) - COALESCE(p.total_paid, 0) AS pending_payment
FROM team_members tm
LEFT JOIN assignment_totals a ON a.team_member_id = tm.team_member_id
LEFT JOIN payment_totals p ON p.team_member_id = tm.team_member_id;
