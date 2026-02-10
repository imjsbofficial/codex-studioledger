# Production House Ledger Data Model & Dashboard Requirements

## Core entities

### Projects
Holds the top-level project (single-day or multi-day).

| Field | Type | Notes |
| --- | --- | --- |
| project_id | UUID | Primary key. |
| project_name | Text | Name shown on dashboard. |
| project_by | Text | Client/vendor name. |
| start_date | Date | First day for the project. |
| end_date | Date | Last day for the project (same as start for single-day). |
| location | Text | Default location for the project. |
| project_amount | Decimal | Total agreed project amount. |
| notes | Text | Optional description. |

### Project Days (Events)
Represents each day for a multi-day project (or a single-day project as one event).

| Field | Type | Notes |
| --- | --- | --- |
| event_id | UUID | Primary key. |
| project_id | UUID | FK → Projects. |
| event_date | Date | Date of the event/day. |
| location | Text | Location for this day. |

### Team Members
Master list of team members.

| Field | Type | Notes |
| --- | --- | --- |
| team_member_id | UUID | Primary key. |
| name | Text | Person name. |
| role | Text | Optional role (camera, editor, etc.). |
| notes | Text | Optional notes. |

### Event Assignments
Connects team members to an event with their per-event rate.

| Field | Type | Notes |
| --- | --- | --- |
| assignment_id | UUID | Primary key. |
| event_id | UUID | FK → Project Days. |
| team_member_id | UUID | FK → Team Members. |
| rate | Decimal | Price for this team member for this event. |

### Vendor Payments (Project-level)
Tracks client/vendor payments received for a project.

| Field | Type | Notes |
| --- | --- | --- |
| vendor_payment_id | UUID | Primary key. |
| project_id | UUID | FK → Projects. |
| payment_date | Date | Date received. |
| amount | Decimal | Payment amount. |
| reference | Text | Optional reference/notes. |

### Team Member Payments
Tracks payments you make to team members (can be multiple transactions).

| Field | Type | Notes |
| --- | --- | --- |
| team_payment_id | UUID | Primary key. |
| team_member_id | UUID | FK → Team Members. |
| event_id | UUID | FK → Project Days. |
| payment_date | Date | Date paid. |
| amount | Decimal | Amount paid. |
| reference | Text | Optional reference/notes. |

### Other Expenses
Non-team expenses (travel, equipment, etc.) tied to a project or event.

| Field | Type | Notes |
| --- | --- | --- |
| expense_id | UUID | Primary key. |
| project_id | UUID | FK → Projects. |
| event_id | UUID | FK → Project Days (nullable). |
| expense_date | Date | Date of expense. |
| amount | Decimal | Expense amount. |
| category | Text | Fuel, hotel, gear rental, etc. |
| notes | Text | Optional notes. |

## Required dashboard metrics

### Project/Event profitability
For each project (and each event day):

- **Project revenue** = sum of vendor payments (project level).
- **Team cost** = sum of assignment rates for all team members assigned to the project/event.
- **Team paid** = sum of team member payments (per project/event).
- **Other expenses** = sum of other expenses for the project/event.
- **Total expense** = team cost + other expenses.
- **Profit** = project revenue - total expense.

### Team member overview
For each team member:

- **Events assigned** = count of event assignments + list of events.
- **Total payment due** = sum of assignment rates across events.
- **Total paid** = sum of payments made.
- **Pending payment** = total payment due - total paid.

## Suggested views / reports

1. **Projects list** with:
   - Date range, project name, location, project by, total project amount.
   - Aggregates: team cost, other expenses, total expense, profit.
2. **Events list** per project:
   - Event date, location, assigned team members, per-event team cost.
3. **Team member ledger**:
   - Each event assigned, rate, paid, pending, totals.
4. **Payments summary**:
   - Vendor payments timeline.
   - Team payment timeline.

## Notes & validation rules

- Single-day projects are stored as one event in **Project Days**.
- Assignment rates are event-specific so different rates can be recorded per event.
- Vendor payments and team payments support multiple transactions per project/event.
- Pending payment is never negative; if overpaid, flag for reconciliation.
