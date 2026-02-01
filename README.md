# Production House Ledger App (Schema + Views)

This repository contains a ready-to-run SQLite schema and reporting views for the Production House Ledger. It covers:

- Single-day and multi-day projects (stored as events).
- Per-event team member assignments and rates.
- Multiple vendor payments per project.
- Multiple payments to team members per event.
- Other project or event expenses.
- Dashboard-friendly views for project profitability and team member balances.

## Files

- `schema.sql`: Database schema and reporting views.
- `project_ledger_spec.md`: Business requirements and reporting definitions.

## Quick start (SQLite)

```bash
sqlite3 ledger.db < schema.sql
```

## Example dashboard queries

```sql
-- Project-level profitability
SELECT * FROM project_financials ORDER BY start_date;

-- Event-level costs
SELECT * FROM event_cost_summary ORDER BY event_date;

-- Team member balances
SELECT * FROM team_member_balances ORDER BY name;
```

## Notes

- Use UUIDs (or any unique string) for primary keys.
- Dates are stored as ISO strings (YYYY-MM-DD) for portability.
- Pending payment shows `total_due - total_paid` and should be monitored for negative values if overpayments occur.
