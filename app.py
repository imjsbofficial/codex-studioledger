from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "data"
DB_PATH = DB_DIR / "ledger.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

app = Flask(__name__)


@app.before_request
def ensure_database() -> None:
    initialize_database()


def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    return conn


def initialize_database() -> None:
    if DB_PATH.exists():
        return

    DB_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        conn.executescript(schema_sql)
        seed_sample_data(conn)


def seed_sample_data(conn: sqlite3.Connection) -> None:
    project_id = str(uuid4())
    event_one_id = str(uuid4())
    event_two_id = str(uuid4())
    team_a_id = str(uuid4())
    team_b_id = str(uuid4())

    conn.execute(
        """
        INSERT INTO projects (
            project_id, project_name, project_by, start_date, end_date, location, project_amount, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            "Brand Launch Campaign",
            "Kite Studios",
            "2025-02-01",
            "2025-02-02",
            "Mumbai",
            150000,
            "Two-day brand launch coverage.",
        ),
    )

    conn.executemany(
        """
        INSERT INTO project_events (event_id, project_id, event_date, location)
        VALUES (?, ?, ?, ?)
        """,
        [
            (event_one_id, project_id, "2025-02-01", "Mumbai Studio"),
            (event_two_id, project_id, "2025-02-02", "Mumbai Outdoor"),
        ],
    )

    conn.executemany(
        """
        INSERT INTO team_members (team_member_id, name, role, notes)
        VALUES (?, ?, ?, ?)
        """,
        [
            (team_a_id, "Asha Nair", "Director", "Lead creative"),
            (team_b_id, "Ravi Mehta", "Cinematographer", "Camera ops"),
        ],
    )

    conn.executemany(
        """
        INSERT INTO event_assignments (assignment_id, event_id, team_member_id, rate)
        VALUES (?, ?, ?, ?)
        """,
        [
            (str(uuid4()), event_one_id, team_a_id, 20000),
            (str(uuid4()), event_one_id, team_b_id, 15000),
            (str(uuid4()), event_two_id, team_a_id, 22000),
            (str(uuid4()), event_two_id, team_b_id, 16000),
        ],
    )

    conn.executemany(
        """
        INSERT INTO vendor_payments (vendor_payment_id, project_id, payment_date, amount, reference)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (str(uuid4()), project_id, "2025-02-01", 50000, "Advance"),
            (str(uuid4()), project_id, "2025-02-05", 100000, "Balance"),
        ],
    )

    conn.executemany(
        """
        INSERT INTO team_member_payments (
            team_payment_id, team_member_id, event_id, payment_date, amount, reference
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (str(uuid4()), team_a_id, event_one_id, "2025-02-03", 10000, "Partial"),
            (str(uuid4()), team_b_id, event_one_id, "2025-02-03", 8000, "Partial"),
        ],
    )

    conn.executemany(
        """
        INSERT INTO other_expenses (
            expense_id, project_id, event_id, expense_date, amount, category, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (str(uuid4()), project_id, event_one_id, "2025-02-01", 5000, "Travel", "Cab fares"),
            (str(uuid4()), project_id, event_two_id, "2025-02-02", 6500, "Equipment", "Lens rental"),
        ],
    )

    conn.commit()


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/projects")
def projects() -> tuple[str, int, dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM project_financials ORDER BY start_date"
        ).fetchall()
    return jsonify(rows)

@app.route("/api/projects", methods=["POST"])
def create_project() -> tuple[str, int, dict]:
    payload = request.get_json(force=True)
    project_id = str(uuid4())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO projects (
                project_id, project_name, project_by, start_date, end_date, location, project_amount, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                payload.get("project_name"),
                payload.get("project_by"),
                payload.get("start_date"),
                payload.get("end_date"),
                payload.get("location"),
                payload.get("project_amount", 0),
                payload.get("notes"),
            ),
        )
        conn.commit()
    return jsonify({"project_id": project_id}), 201, {"Content-Type": "application/json"}


@app.route("/api/projects/<project_id>", methods=["PUT"])
def update_project(project_id: str) -> tuple[str, int, dict]:
    payload = request.get_json(force=True)
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE projects
            SET project_name = ?,
                project_by = ?,
                start_date = ?,
                end_date = ?,
                location = ?,
                project_amount = ?,
                notes = ?
            WHERE project_id = ?
            """,
            (
                payload.get("project_name"),
                payload.get("project_by"),
                payload.get("start_date"),
                payload.get("end_date"),
                payload.get("location"),
                payload.get("project_amount", 0),
                payload.get("notes"),
                project_id,
            ),
        )
        conn.commit()
    return jsonify({"status": "ok"}), 200, {"Content-Type": "application/json"}


@app.route("/api/projects/<project_id>", methods=["DELETE"])
def delete_project(project_id: str) -> tuple[str, int, dict]:
    with get_connection() as conn:
        conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
        conn.commit()
    return jsonify({"status": "deleted"}), 200, {"Content-Type": "application/json"}


@app.route("/api/events")
def events() -> tuple[str, int, dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM event_cost_summary ORDER BY event_date"
        ).fetchall()
    return jsonify(rows)

@app.route("/api/events", methods=["POST"])
def create_event() -> tuple[str, int, dict]:
    payload = request.get_json(force=True)
    event_id = str(uuid4())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO project_events (event_id, project_id, event_date, location)
            VALUES (?, ?, ?, ?)
            """,
            (
                event_id,
                payload.get("project_id"),
                payload.get("event_date"),
                payload.get("location"),
            ),
        )
        conn.commit()
    return jsonify({"event_id": event_id}), 201, {"Content-Type": "application/json"}


@app.route("/api/events/<event_id>", methods=["PUT"])
def update_event(event_id: str) -> tuple[str, int, dict]:
    payload = request.get_json(force=True)
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE project_events
            SET project_id = ?,
                event_date = ?,
                location = ?
            WHERE event_id = ?
            """,
            (
                payload.get("project_id"),
                payload.get("event_date"),
                payload.get("location"),
                event_id,
            ),
        )
        conn.commit()
    return jsonify({"status": "ok"}), 200, {"Content-Type": "application/json"}


@app.route("/api/events/<event_id>", methods=["DELETE"])
def delete_event(event_id: str) -> tuple[str, int, dict]:
    with get_connection() as conn:
        conn.execute("DELETE FROM project_events WHERE event_id = ?", (event_id,))
        conn.commit()
    return jsonify({"status": "deleted"}), 200, {"Content-Type": "application/json"}


@app.route("/api/team-members")
def team_members() -> tuple[str, int, dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM team_member_balances ORDER BY name"
        ).fetchall()
    return jsonify(rows)

@app.route("/api/team-members", methods=["POST"])
def create_team_member() -> tuple[str, int, dict]:
    payload = request.get_json(force=True)
    team_member_id = str(uuid4())
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO team_members (team_member_id, name, role, notes)
            VALUES (?, ?, ?, ?)
            """,
            (
                team_member_id,
                payload.get("name"),
                payload.get("role"),
                payload.get("notes"),
            ),
        )
        conn.commit()
    return jsonify({"team_member_id": team_member_id}), 201, {"Content-Type": "application/json"}


@app.route("/api/team-members/<team_member_id>", methods=["PUT"])
def update_team_member(team_member_id: str) -> tuple[str, int, dict]:
    payload = request.get_json(force=True)
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE team_members
            SET name = ?,
                role = ?,
                notes = ?
            WHERE team_member_id = ?
            """,
            (
                payload.get("name"),
                payload.get("role"),
                payload.get("notes"),
                team_member_id,
            ),
        )
        conn.commit()
    return jsonify({"status": "ok"}), 200, {"Content-Type": "application/json"}


@app.route("/api/team-members/<team_member_id>", methods=["DELETE"])
def delete_team_member(team_member_id: str) -> tuple[str, int, dict]:
    with get_connection() as conn:
        conn.execute("DELETE FROM team_members WHERE team_member_id = ?", (team_member_id,))
        conn.commit()
    return jsonify({"status": "deleted"}), 200, {"Content-Type": "application/json"}


@app.route("/api/projects/<project_id>/events")
def project_events(project_id: str) -> tuple[str, int, dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT e.*
            FROM event_cost_summary e
            WHERE e.project_id = ?
            ORDER BY e.event_date
            """,
            (project_id,),
        ).fetchall()
    return jsonify(rows)


@app.route("/api/health")
def health() -> tuple[str, int, dict]:
    return json.dumps({"status": "ok"}), 200, {"Content-Type": "application/json"}


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=False)
