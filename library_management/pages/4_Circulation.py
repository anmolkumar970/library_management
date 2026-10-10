"""
pages/4_Circulation.py — Borrow & Return
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import database as db
from utils import fmt_date, status_badge, days_overdue

st.set_page_config(page_title="Circulation — LibraryMS", page_icon="🔄", layout="wide")
db.init_db()
db.refresh_overdue()

st.title("🔄 Circulation — Borrow & Return")
st.markdown("---")

tab_borrow, tab_return, tab_active, tab_all = st.tabs([
    "📤 Issue Book", "📥 Return Book", "⏳ Active Borrowings", "📋 All Records"
])

# ── ISSUE ─────────────────────────────────────────────────────────────────────
with tab_borrow:
    st.subheader("Issue a Book to a Member")

    members = db.get_all_members(status="Active")
    books   = [b for b in db.get_all_books() if b["available_copies"] > 0]

    if not members:
        st.warning("No active members registered.")
    elif not books:
        st.warning("No books currently available.")
    else:
        with st.form("borrow_form"):
            mem_map  = {f"{m['name']} (ID {m['id']})": m["id"] for m in members}
            book_map = {f"{b['title']} — {b['author']} [{b['available_copies']} avail.]": b["id"] for b in books}

            mem_sel  = st.selectbox("Member *", list(mem_map.keys()))
            book_sel = st.selectbox("Book *",   list(book_map.keys()))
            c1, c2   = st.columns(2)
            borrow_d = c1.date_input("Borrow Date", value=date.today())
            due_d    = c2.date_input("Due Date",    value=date.today() + timedelta(days=14))
            submit   = st.form_submit_button("Issue Book")

        if submit:
            if due_d <= borrow_d:
                st.error("Due date must be after borrow date.")
            else:
                db.borrow_book(book_map[book_sel], mem_map[mem_sel], str(borrow_d), str(due_d))
                st.success(f"✅ Book issued to **{mem_sel.split(' (')[0]}**. Due: {due_d.strftime('%d %b %Y')}")
                st.rerun()

# ── RETURN ────────────────────────────────────────────────────────────────────
with tab_return:
    st.subheader("Process a Return")

    active = db.get_active_borrowings()
    if not active:
        st.info("No books currently on loan.")
    else:
        with st.form("return_form"):
            ret_map = {
                f"{r['book_title']} → {r['member_name']} (due {fmt_date(r['due_date'])})": r["id"]
                for r in active
            }
            ret_sel  = st.selectbox("Select borrowing record *", list(ret_map.keys()))
            ret_date = st.date_input("Return Date", value=date.today())
            submit2  = st.form_submit_button("Process Return")

        if submit2:
            db.return_book(ret_map[ret_sel], str(ret_date))
            st.success("✅ Book returned successfully.")
            st.rerun()

# ── ACTIVE ────────────────────────────────────────────────────────────────────
with tab_active:
    st.subheader("Active & Overdue Borrowings")
    active = db.get_active_borrowings()
    if active:
        rows = []
        for r in active:
            od = days_overdue(r["due_date"])
            rows.append({
                "Book":        r["book_title"],
                "Member":      r["member_name"],
                "Borrowed":    fmt_date(r["borrow_date"]),
                "Due":         fmt_date(r["due_date"]),
                "Days Overdue": od if od > 0 else 0,
                "Status":      status_badge(r["status"]),
            })
        df = pd.DataFrame(rows)
        df.index = range(1, len(df) + 1)
        st.dataframe(df, use_container_width=True)
        overdue_count = sum(1 for r in active if r["status"] == "Overdue")
        if overdue_count:
            st.error(f"⚠️ {overdue_count} overdue borrowing(s) require attention.")
    else:
        st.success("🎉 No active borrowings.")

# ── ALL RECORDS ────────────────────────────────────────────────────────────────
with tab_all:
    st.subheader("Full Borrowing History")
    all_b = db.get_all_borrowings()
    if all_b:
        df2 = pd.DataFrame(all_b)
        df2["borrow_date"] = df2["borrow_date"].apply(fmt_date)
        df2["due_date"]    = df2["due_date"].apply(fmt_date)
        df2["return_date"] = df2["return_date"].apply(fmt_date)
        df2["Status"]      = df2["status"].apply(status_badge)
        st.dataframe(
            df2[["book_title", "member_name", "borrow_date", "due_date", "return_date", "Status"]].rename(columns={
                "book_title": "Book", "member_name": "Member",
                "borrow_date": "Borrowed", "due_date": "Due", "return_date": "Returned"
            }),
            use_container_width=True,
        )
        st.caption(f"{len(all_b)} total borrowing record(s).")
    else:
        st.info("No borrowing records yet.")
