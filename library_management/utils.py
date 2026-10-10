"""
utils.py — Shared helpers for the Library Management System
"""

from datetime import date, datetime


def today_str() -> str:
    return str(date.today())


def due_date_str(loan_days: int = 14) -> str:
    from datetime import timedelta
    return str(date.today() + timedelta(days=loan_days))


def fmt_date(val) -> str:
    """Return a human-friendly date string, or '—' if empty."""
    if not val:
        return "—"
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").strftime("%d %b %Y")
    except ValueError:
        return str(val)


def days_overdue(due_date_str: str) -> int:
    """Return how many days past due (positive = overdue, negative = days left)."""
    try:
        due = datetime.strptime(due_date_str, "%Y-%m-%d").date()
        return (date.today() - due).days
    except ValueError:
        return 0


def status_badge(status: str) -> str:
    colours = {
        "Active":    "🟢",
        "Suspended": "🔴",
        "Borrowed":  "🔵",
        "Returned":  "✅",
        "Overdue":   "🔴",
    }
    return f"{colours.get(status, '⚪')} {status}"
