"""
app.py — Library Management System
====================================
Entry point. Run with:
    streamlit run library_management/app.py
"""

import sys
from pathlib import Path

# Make sure sibling modules are importable when run from any directory
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd

import database as db
from utils import fmt_date, status_badge

# ── one-time DB init ──────────────────────────────────────────────────────────
db.init_db()
db.refresh_overdue()

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── sidebar branding ─────────────────────────────────────────────────────────
st.sidebar.title("📚 LibraryMS")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "Navigate using the **Pages** menu above, or use the links below.",
    unsafe_allow_html=True,
)
st.sidebar.markdown("""
- 📖 [Books](./Books)
- 🏷️ [Categories](./Categories)
- 👤 [Members](./Members)
- 🔄 [Circulation](./Circulation)
- 📊 [Trends](./Trends)
""")

# ── dashboard home ────────────────────────────────────────────────────────────
st.title("📚 Library Management System")
st.markdown("Welcome! Use the sidebar to navigate between modules.")
st.markdown("---")

summary = db.dashboard_summary()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Total Copies",     summary["total_books"])
c2.metric("✅ Available",         summary["available"])
c3.metric("👤 Members",           summary["total_members"])
c4.metric("🔵 Active Borrows",    summary["active_borrows"])
c5.metric("🔴 Overdue",           summary["overdue"],
          delta=f"-{summary['overdue']}" if summary["overdue"] else None,
          delta_color="inverse")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🔥 Top Borrowed Books")
    top = db.trend_top_books(5)
    if top:
        df = pd.DataFrame(top)
        df.index = range(1, len(df) + 1)
        st.dataframe(df[["title", "author", "borrow_count"]].rename(columns={
            "title": "Title", "author": "Author", "borrow_count": "Borrows"
        }), use_container_width=True)

with col_right:
    st.subheader("⏰ Active & Overdue Borrowings")
    active = db.get_active_borrowings()
    if active:
        df2 = pd.DataFrame(active)
        df2["Due"] = df2["due_date"].apply(fmt_date)
        df2["Status"] = df2["status"].apply(status_badge)
        st.dataframe(
            df2[["book_title", "member_name", "Due", "Status"]].rename(columns={
                "book_title": "Book", "member_name": "Member"
            }),
            use_container_width=True,
        )
    else:
        st.info("No active borrowings.")
