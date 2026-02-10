# Production House Ledger App

This repository contains a ready-to-run SQLite schema, Flask API, and a lightweight dashboard UI for the Production House Ledger. It covers:

- Single-day and multi-day projects (stored as events).
- Per-event team member assignments and rates.
- Multiple vendor payments per project.
- Multiple payments to team members per event.
- Other project or event expenses.
- Dashboard-friendly views for project profitability and team member balances.

## Files

- `schema.sql`: Database schema and reporting views.
- `project_ledger_spec.md`: Business requirements and reporting definitions.
- `app.py`: Flask API + dashboard UI.
- `templates/index.html`: Dashboard layout.
- `static/styles.css`: Dashboard styling.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open <http://localhost:5000> to view the dashboard.

The app creates `data/ledger.db` on first run using `schema.sql` and seeds a small sample dataset.

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
