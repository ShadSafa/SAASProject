#!/usr/bin/env python3
"""
update_kanban.py
────────────────
Reads .planning/STATE.md, determines which plans are complete, and updates:
  1. kanban.html   — the embedded STATE object (for offline / file:// viewing)
  2. kanban-state.json — machine-readable state file (for browser auto-polling)

Usage:
    python .planning/update_kanban.py

Git hook (auto-run after every commit):
    echo 'python .planning/update_kanban.py' >> .git/hooks/post-commit
    chmod +x .git/hooks/post-commit          # macOS/Linux only
"""

import re
import json
from pathlib import Path
from datetime import date

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT       = Path(__file__).resolve().parent.parent
STATE_MD   = ROOT / ".planning" / "STATE.md"
KANBAN_HTML = ROOT / "kanban.html"
KANBAN_JSON = ROOT / "kanban-state.json"

# ── Full plan catalogue (source of truth for name/phase/seq/total) ─────────
# status is computed dynamically from STATE.md — do not edit the status field here
PLANS = [
    # Phase 1
    dict(id="01-01", phase=1, phaseName="Foundation & Database",         seq=1,  total=10, name="Database Schema & Migrations"),
    dict(id="01-02", phase=1, phaseName="Foundation & Database",         seq=2,  total=10, name="Email Service Integration (Resend)"),
    dict(id="01-03", phase=1, phaseName="Foundation & Database",         seq=3,  total=10, name="Authentication Services (Argon2id, JWT)"),
    dict(id="01-04", phase=1, phaseName="Foundation & Database",         seq=4,  total=10, name="React Frontend Foundation"),
    dict(id="01-05", phase=1, phaseName="Foundation & Database",         seq=5,  total=10, name="Auth API Endpoints"),
    dict(id="01-06", phase=1, phaseName="Foundation & Database",         seq=6,  total=10, name="Frontend Signup & Login Pages"),
    dict(id="01-07", phase=1, phaseName="Foundation & Database",         seq=7,  total=10, name="Backend Password Reset"),
    dict(id="01-08", phase=1, phaseName="Foundation & Database",         seq=8,  total=10, name="Frontend Password Reset Pages"),
    dict(id="01-09", phase=1, phaseName="Foundation & Database",         seq=9,  total=10, name="Backend Profile Management & Account Deletion"),
    dict(id="01-10", phase=1, phaseName="Foundation & Database",         seq=10, total=10, name="Frontend Profile Page"),
    # Phase 2
    dict(id="02-01", phase=2, phaseName="Instagram Integration",         seq=1,  total=6,  name="Instagram OAuth Backend Endpoints"),
    dict(id="02-02", phase=2, phaseName="Instagram Integration",         seq=2,  total=6,  name="Token Storage & Encryption"),
    dict(id="02-03", phase=2, phaseName="Instagram Integration",         seq=3,  total=6,  name="Token Auto-Refresh Background Job"),
    dict(id="02-04", phase=2, phaseName="Instagram Integration",         seq=4,  total=6,  name="Multiple Account Data Model"),
    dict(id="02-05", phase=2, phaseName="Instagram Integration",         seq=5,  total=6,  name="Connection Status API Endpoints"),
    dict(id="02-06", phase=2, phaseName="Instagram Integration",         seq=6,  total=6,  name="Frontend Instagram Connection UI"),
    # Phase 3
    dict(id="03-01", phase=3, phaseName="Core Scanning Engine",          seq=1,  total=9,  name="Third-Party API Integration (Apify)"),
    dict(id="03-02", phase=3, phaseName="Core Scanning Engine",          seq=2,  total=9,  name="PhantomBuster Fallback Implementation"),
    dict(id="03-03", phase=3, phaseName="Core Scanning Engine",          seq=3,  total=9,  name="Growth Velocity Algorithm"),
    dict(id="03-04", phase=3, phaseName="Core Scanning Engine",          seq=4,  total=9,  name="URL Parsing & Single-Post Analysis"),
    dict(id="03-05", phase=3, phaseName="Core Scanning Engine",          seq=5,  total=9,  name="Scan Job Orchestration (Background Workers)"),
    dict(id="03-06", phase=3, phaseName="Core Scanning Engine",          seq=6,  total=9,  name="Scan Result Storage"),
    dict(id="03-07", phase=3, phaseName="Core Scanning Engine",          seq=7,  total=9,  name="Frontend Scan Trigger UI"),
    dict(id="03-08", phase=3, phaseName="Core Scanning Engine",          seq=8,  total=9,  name="Summary Card Component"),
    dict(id="03-09", phase=3, phaseName="Core Scanning Engine",          seq=9,  total=9,  name="Loading & Progress States"),
    # Phase 4
    dict(id="04-01", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=1,  total=10, name="OpenAI API Integration"),
    dict(id="04-02", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=2,  total=10, name="Prompt Engineering for Viral Analysis"),
    dict(id="04-03", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=3,  total=10, name="Hook Analysis (Video Thumbnails & Captions)"),
    dict(id="04-04", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=4,  total=10, name="Emotional Trigger Taxonomy"),
    dict(id="04-05", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=5,  total=10, name="Engagement Velocity Calculations"),
    dict(id="04-06", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=6,  total=10, name="Hashtag Performance Metrics"),
    dict(id="04-07", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=7,  total=10, name="Comment Sentiment Analysis"),
    dict(id="04-08", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=8,  total=10, name="Analysis Caching Layer"),
    dict(id="04-09", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=9,  total=10, name="Structured Output Validation"),
    dict(id="04-10", phase=4, phaseName="AI Analysis \u2014 Algorithm Factors", seq=10, total=10, name="Cost Monitoring"),
    # Phase 5
    dict(id="05-01", phase=5, phaseName="AI Analysis \u2014 Content Deep Dive", seq=1,  total=7,  name="Demographics Extraction from Instagram Data"),
    dict(id="05-02", phase=5, phaseName="AI Analysis \u2014 Content Deep Dive", seq=2,  total=7,  name="Engagement Rate Formulas"),
    dict(id="05-03", phase=5, phaseName="AI Analysis \u2014 Content Deep Dive", seq=3,  total=7,  name="Interest Inference Logic"),
    dict(id="05-04", phase=5, phaseName="AI Analysis \u2014 Content Deep Dive", seq=4,  total=7,  name="Content Type Taxonomy (Native & Extended)"),
    dict(id="05-05", phase=5, phaseName="AI Analysis \u2014 Content Deep Dive", seq=5,  total=7,  name="Niche Detection with OpenAI"),
    dict(id="05-06", phase=5, phaseName="AI Analysis \u2014 Content Deep Dive", seq=6,  total=7,  name="User Niche Override UI"),
    dict(id="05-07", phase=5, phaseName="AI Analysis \u2014 Content Deep Dive", seq=7,  total=7,  name="Content Categorization Storage"),
    # Phase 6
    dict(id="06-01", phase=6, phaseName="User Interface & Display",      seq=1,  total=6,  name="Summary Card Enhancement (All Metrics)"),
    dict(id="06-02", phase=6, phaseName="User Interface & Display",      seq=2,  total=6,  name="Detailed Analysis View Component"),
    dict(id="06-03", phase=6, phaseName="User Interface & Display",      seq=3,  total=6,  name="Drill-Down Modal & Page Routing"),
    dict(id="06-04", phase=6, phaseName="User Interface & Display",      seq=4,  total=6,  name="Data Visualization Components (Charts)"),
    dict(id="06-05", phase=6, phaseName="User Interface & Display",      seq=5,  total=6,  name="External Link Handling"),
    dict(id="06-06", phase=6, phaseName="User Interface & Display",      seq=6,  total=6,  name="Responsive Design Polish"),
    # Phase 7
    dict(id="07-01", phase=7, phaseName="Filtering & Search",            seq=1,  total=5,  name="Filter API Endpoints (Query Builder)"),
    dict(id="07-02", phase=7, phaseName="Filtering & Search",            seq=2,  total=5,  name="Filter UI Components (Dropdowns, Ranges)"),
    dict(id="07-03", phase=7, phaseName="Filtering & Search",            seq=3,  total=5,  name="Search Functionality"),
    dict(id="07-04", phase=7, phaseName="Filtering & Search",            seq=4,  total=5,  name="Filter State Management"),
    dict(id="07-05", phase=7, phaseName="Filtering & Search",            seq=5,  total=5,  name="Performance Optimization & Indexing"),
    # Phase 8
    dict(id="08-01", phase=8, phaseName="Export System",                 seq=1,  total=7,  name="PDF Generation Service (ReportLab)"),
    dict(id="08-02", phase=8, phaseName="Export System",                 seq=2,  total=7,  name="CSV Export Endpoint"),
    dict(id="08-03", phase=8, phaseName="Export System",                 seq=3,  total=7,  name="Shareable Link System (Token Generation)"),
    dict(id="08-04", phase=8, phaseName="Export System",                 seq=4,  total=7,  name="Public Share Page (Unauthenticated Access)"),
    dict(id="08-05", phase=8, phaseName="Export System",                 seq=5,  total=7,  name="Password Protection for Links"),
    dict(id="08-06", phase=8, phaseName="Export System",                 seq=6,  total=7,  name="Link Revocation API"),
    dict(id="08-07", phase=8, phaseName="Export System",                 seq=7,  total=7,  name="Export UI Controls"),
    # Phase 9
    dict(id="09-01", phase=9, phaseName="Historical Data & Trends",      seq=1,  total=7,  name="Scan History List UI"),
    dict(id="09-02", phase=9, phaseName="Historical Data & Trends",      seq=2,  total=7,  name="Scan Archive Viewer"),
    dict(id="09-03", phase=9, phaseName="Historical Data & Trends",      seq=3,  total=7,  name="Time-Series Queries (TimescaleDB)"),
    dict(id="09-04", phase=9, phaseName="Historical Data & Trends",      seq=4,  total=7,  name="Trend Visualization Components (Recharts)"),
    dict(id="09-05", phase=9, phaseName="Historical Data & Trends",      seq=5,  total=7,  name="Comparison View (Side-by-Side)"),
    dict(id="09-06", phase=9, phaseName="Historical Data & Trends",      seq=6,  total=7,  name="Trending Algorithms"),
    dict(id="09-07", phase=9, phaseName="Historical Data & Trends",      seq=7,  total=7,  name="Delete Scan Functionality"),
    # Phase 10
    dict(id="10-01", phase=10, phaseName="Subscription & Monetization",  seq=1,  total=9,  name="Stripe Integration (API Keys, SDK)"),
    dict(id="10-02", phase=10, phaseName="Subscription & Monetization",  seq=2,  total=9,  name="Subscription Tier Data Model"),
    dict(id="10-03", phase=10, phaseName="Subscription & Monetization",  seq=3,  total=9,  name="Usage Tracking (Scans per User per Month)"),
    dict(id="10-04", phase=10, phaseName="Subscription & Monetization",  seq=4,  total=9,  name="Limit Enforcement Middleware"),
    dict(id="10-05", phase=10, phaseName="Subscription & Monetization",  seq=5,  total=9,  name="Stripe Checkout Flow"),
    dict(id="10-06", phase=10, phaseName="Subscription & Monetization",  seq=6,  total=9,  name="Webhook Endpoint & Handlers"),
    dict(id="10-07", phase=10, phaseName="Subscription & Monetization",  seq=7,  total=9,  name="Billing Portal Link"),
    dict(id="10-08", phase=10, phaseName="Subscription & Monetization",  seq=8,  total=9,  name="Pricing Page UI"),
    dict(id="10-09", phase=10, phaseName="Subscription & Monetization",  seq=9,  total=9,  name="Email Notifications (Subscription Events)"),
    # Phase 11
    dict(id="11-01", phase=11, phaseName="Polish & Launch Preparation",  seq=1,  total=6,  name="End-to-End Testing Suite"),
    dict(id="11-02", phase=11, phaseName="Polish & Launch Preparation",  seq=2,  total=6,  name="Performance Profiling & Optimization"),
    dict(id="11-03", phase=11, phaseName="Polish & Launch Preparation",  seq=3,  total=6,  name="Production Environment Setup"),
    dict(id="11-04", phase=11, phaseName="Polish & Launch Preparation",  seq=4,  total=6,  name="Deployment Automation (CI/CD)"),
    dict(id="11-05", phase=11, phaseName="Polish & Launch Preparation",  seq=5,  total=6,  name="Monitoring Setup (Sentry, Logs)"),
    dict(id="11-06", phase=11, phaseName="Polish & Launch Preparation",  seq=6,  total=6,  name="User Documentation"),
]


# ── Parse STATE.md ─────────────────────────────────────────────────────────

def parse_state(path: Path) -> tuple[int, set[str]]:
    """Return (current_phase_number, set_of_completed_plan_ids)."""
    content = path.read_text(encoding="utf-8")

    # Current phase number — matches "**Phase:** 01 - ..." or "**Current Phase:** 01"
    m = re.search(r"\*\*(?:Current )?Phase:\*\*\s+0*(\d+)", content)
    current_phase = int(m.group(1)) if m else 1

    # Completed plan IDs — matches "✓ Plan 01-06:" or "✓ 01-06" etc.
    completed = set(re.findall(r"✓\s+(?:Plan\s+)?(\d{2}-\d{2})", content))

    return current_phase, completed


# ── Status logic ───────────────────────────────────────────────────────────

def compute_status(plan: dict, current_phase: int, completed_ids: set[str]) -> str:
    p = plan["phase"]
    if p < current_phase:
        return "completed"
    if p > current_phase:
        return "pending"
    # p == current_phase
    return "current_complete" if plan["id"] in completed_ids else "current_pending"


# ── Generate JS STATE block ────────────────────────────────────────────────

def build_js_state(current_phase: int, completed_ids: set[str], today: str) -> str:
    lines = []
    lines.append(f'const STATE = {{')
    lines.append(f'  project:      "Instagram Viral Content Analyzer",')
    lines.append(f'  milestone:    "v1.0",')
    lines.append(f'  lastUpdated:  "{today}",')
    lines.append(f'  currentPhase: {current_phase},')
    lines.append(f'  plans: [')

    current_phase_name = None
    for p in PLANS:
        status = compute_status(p, current_phase, completed_ids)
        if p["phaseName"] != current_phase_name:
            current_phase_name = p["phaseName"]
            lines.append(f'    // \u2500\u2500 Phase {p["phase"]} \u2014 {p["phaseName"]} {"─" * max(0, 40 - len(p["phaseName"]))}')
        phase_name_js = p["phaseName"].replace('"', '\\"')
        name_js = p["name"].replace('"', '\\"')
        lines.append(
            f'    {{id:"{p["id"]}",phase:{p["phase"]},phaseName:"{phase_name_js}",'
            f'seq:{p["seq"]},total:{p["total"]},name:"{name_js}",status:"{status}"}},'
        )

    lines.append(f'  ]')
    lines.append(f'}};')
    return "\n".join(lines)


# ── Update kanban.html ─────────────────────────────────────────────────────

MARKER_BEGIN = "// === BEGIN KANBAN STATE (auto-updated by .planning/update_kanban.py)"
MARKER_END   = "// === END KANBAN STATE ==="

def update_html(js_state: str) -> None:
    html = KANBAN_HTML.read_text(encoding="utf-8")
    start = html.find(MARKER_BEGIN)
    end   = html.find(MARKER_END)
    if start == -1 or end == -1:
        print("[update_kanban] ERROR: State markers not found in kanban.html")
        return
    end += len(MARKER_END)
    new_block = f"{MARKER_BEGIN}\n{js_state}\n{MARKER_END}"
    updated = html[:start] + new_block + html[end:]
    KANBAN_HTML.write_text(updated, encoding="utf-8")
    print(f"[update_kanban] kanban.html updated ({KANBAN_HTML})")


# ── Write kanban-state.json ────────────────────────────────────────────────

def write_json(current_phase: int, completed_ids: set[str], today: str) -> None:
    state = {
        "project":      "Instagram Viral Content Analyzer",
        "milestone":    "v1.0",
        "lastUpdated":  today,
        "currentPhase": current_phase,
        "plans": [
            {**p, "status": compute_status(p, current_phase, completed_ids)}
            for p in PLANS
        ],
    }
    KANBAN_JSON.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[update_kanban] kanban-state.json updated ({KANBAN_JSON})")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    if not STATE_MD.exists():
        print(f"[update_kanban] ERROR: STATE.md not found at {STATE_MD}")
        return

    today = date.today().isoformat()
    current_phase, completed_ids = parse_state(STATE_MD)

    print(f"[update_kanban] Current phase: {current_phase}  |  Completed plans: {sorted(completed_ids)}")

    js_state = build_js_state(current_phase, completed_ids, today)
    update_html(js_state)
    write_json(current_phase, completed_ids, today)

    # Summary
    statuses = [compute_status(p, current_phase, completed_ids) for p in PLANS]
    counts = {s: statuses.count(s) for s in ("pending", "current_pending", "current_complete", "completed")}
    print(f"[update_kanban] Cards -> pending:{counts['pending']}  "
          f"cur_pending:{counts['current_pending']}  "
          f"cur_complete:{counts['current_complete']}  "
          f"completed:{counts['completed']}")


if __name__ == "__main__":
    main()
