"""
Idhar Waitlist — backend
Serves the waitlist landing page and stores signups in Supabase (Postgres),
via Supabase's REST API (PostgREST) — no ORM/driver needed, so it works the
same way whether this runs as a long-lived process (Render) or a serverless
function (Vercel).

Required environment variables (see .env.example):
    SUPABASE_URL          e.g. https://xxxxxxxx.supabase.co
    SUPABASE_SERVICE_KEY  the "service_role" secret key (NEVER the anon key,
                           and never expose this to the browser)

Run locally:
    pip install -r requirements.txt
    cp .env.example .env   # then fill in your Supabase values
    python app.py
Then open http://127.0.0.1:5000
"""

import os
import re

import requests
from flask import Flask, jsonify, render_template, request

try:
    from dotenv import load_dotenv

    load_dotenv()  # no-op in production if there's no .env file present
except ImportError:
    pass

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
TABLE = "waitlist_signups"
REST_ENDPOINT = f"{SUPABASE_URL}/rest/v1/{TABLE}"

HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json",
}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_AGE_GROUPS = {"13-17", "18-24", "25-34", "35-44", "45-54", "55+"}
ALLOWED_ROLES = {"founder", "aspiring", "shopper", "counsellor"}

# Shown alongside the real count so the counter doesn't read "0" on day one.
BASE_OFFSET = 50


def _configured():
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/count")
def api_count():
    if not _configured():
        return jsonify({"count": BASE_OFFSET})

    try:
        r = requests.get(
            REST_ENDPOINT,
            headers={**HEADERS, "Prefer": "count=exact", "Range-Unit": "items", "Range": "0-0"},
            params={"select": "id"},
            timeout=8,
        )
        total = 0
        content_range = r.headers.get("Content-Range")  # e.g. "0-0/215"
        if content_range and "/" in content_range:
            total = int(content_range.split("/")[-1])
        return jsonify({"count": total + BASE_OFFSET})
    except (requests.RequestException, ValueError):
        return jsonify({"count": BASE_OFFSET})


@app.route("/api/submit", methods=["POST"])
def api_submit():
    if not _configured():
        return jsonify({"ok": False, "errors": {"_server": "Waitlist storage isn't configured yet."}}), 500

    payload = request.get_json(silent=True) or request.form

    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    age_group = (payload.get("age_group") or "").strip()
    role = (payload.get("role") or "").strip()
    message = (payload.get("message") or "").strip()

    errors = {}
    if not name or len(name) < 2:
        errors["name"] = "Enter your full name."
    if not email or not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."
    if age_group not in ALLOWED_AGE_GROUPS:
        errors["age_group"] = "Choose an age group."
    if role not in ALLOWED_ROLES:
        errors["role"] = "Tell us which one describes you."

    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    row = {
        "name": name,
        "email": email,
        "age_group": age_group,
        "role": role,
        "message": message or None,
    }

    try:
        r = requests.post(
            REST_ENDPOINT,
            headers={**HEADERS, "Prefer": "return=representation"},
            json=row,
            timeout=8,
        )
    except requests.RequestException:
        return jsonify({"ok": False, "errors": {"_server": "Couldn't reach the database. Try again shortly."}}), 502

    if r.status_code == 201:
        count_resp = api_count()
        count = count_resp.get_json().get("count")
        return jsonify({"ok": True, "count": count})

    # Unique-constraint violation on email = already on the list.
    if r.status_code == 409:
        return jsonify(
            {"ok": False, "already_joined": True, "message": "You're already on the list — we'll be in touch."}
        ), 200

    return jsonify({"ok": False, "errors": {"_server": "Something went wrong saving your entry."}}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True, port=5000)
