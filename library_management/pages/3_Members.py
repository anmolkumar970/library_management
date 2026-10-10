"""
pages/3_Members.py — Member Management
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import date
import database as db
from utils import fmt_date, status_badge

st.set_page_config(page_title="Members — LibraryMS", page_icon="👤", layout="wide")
db.init_db()

st.title("👤 Members")
st.markdown("---")

# ── Search / filter ───────────────────────────────────────────────────────────
col_s, col_st = st.columns([3, 1])
search   = col_s.text_input("🔍 Search by name or email", "")
status_f = col_st.selectbox("Status", ["All", "Active", "Suspended"])

members  = db.get_all_members(search=search, status=None if status_f == "All" else status_f)

# ── Table ─────────────────────────────────────────────────────────────────────
if members:
    df = pd.DataFrame(members)
    df["join_date"] = df["join_date"].apply(fmt_date)
    df["Status"]    = df["status"].apply(status_badge)
    display = df[["name", "email", "phone", "join_date", "Status"]].rename(columns={
        "name": "Name", "email": "Email", "phone": "Phone", "join_date": "Member Since"
    })
    display.index = range(1, len(display) + 1)
    st.dataframe(display, use_container_width=True)
    st.caption(f"{len(members)} member(s) found.")
else:
    st.info("No members match your search.")

st.markdown("---")

tab_add, tab_edit, tab_del, tab_hist = st.tabs([
    "➕ Add Member", "✏️ Edit Member", "🗑️ Delete Member", "📋 Borrowing History"
])

# ── ADD ──────────────────────────────────────────────────────────────────────
with tab_add:
    with st.form("add_member_form"):
        st.subheader("Register New Member")
        c1, c2 = st.columns(2)
        name   = c1.text_input("Full Name *")
        email  = c2.text_input("Email")
        phone  = c1.text_input("Phone")
        jdate  = c2.date_input("Join Date", value=date.today())
        status = st.selectbox("Status", ["Active", "Suspended"])
        ok     = st.form_submit_button("Register")
    if ok:
        if not name:
            st.error("Name is required.")
        else:
            try:
                db.add_member(name, email, phone, str(jdate), status)
                st.success(f"✅ Member '{name}' registered.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ── EDIT ─────────────────────────────────────────────────────────────────────
with tab_edit:
    st.subheader("Edit Member")
    all_members = db.get_all_members()
    if all_members:
        sel_map = {f"{m['name']} (ID {m['id']})": m["id"] for m in all_members}
        sel     = st.selectbox("Select member", list(sel_map.keys()), key="edit_mem_sel")
        m       = db.get_member(sel_map[sel])
        if m:
            with st.form("edit_member_form"):
                c1, c2  = st.columns(2)
                e_name  = c1.text_input("Name",  value=m["name"])
                e_email = c2.text_input("Email", value=m["email"] or "")
                e_phone = c1.text_input("Phone", value=m["phone"] or "")
                e_status = st.selectbox("Status", ["Active", "Suspended"],
                                        index=0 if m["status"] == "Active" else 1)
                save = st.form_submit_button("Save")
            if save:
                db.update_member(m["id"], e_name, e_email, e_phone, e_status)
                st.success("✅ Member updated.")
                st.rerun()

# ── DELETE ────────────────────────────────────────────────────────────────────
with tab_del:
    st.subheader("Delete Member")
    all_members = db.get_all_members()
    if all_members:
        del_map = {f"{m['name']} (ID {m['id']})": m["id"] for m in all_members}
        del_sel = st.selectbox("Select member", list(del_map.keys()), key="del_mem_sel")
        st.warning("This will permanently remove the member record.")
        if st.button("🗑️ Delete Member", type="primary"):
            db.delete_member(del_map[del_sel])
            st.success("Member deleted.")
            st.rerun()

# ── HISTORY ──────────────────────────────────────────────────────────────────
with tab_hist:
    st.subheader("Member Borrowing History")
    all_members = db.get_all_members()
    if all_members:
        hist_map = {f"{m['name']} (ID {m['id']})": m["id"] for m in all_members}
        hist_sel = st.selectbox("Select member", list(hist_map.keys()), key="hist_mem_sel")
        hist     = db.get_member_borrowings(hist_map[hist_sel])
        if hist:
            df2 = pd.DataFrame(hist)
            df2["borrow_date"]  = df2["borrow_date"].apply(fmt_date)
            df2["due_date"]     = df2["due_date"].apply(fmt_date)
            df2["return_date"]  = df2["return_date"].apply(fmt_date)
            df2["Status"]       = df2["status"].apply(status_badge)
            st.dataframe(
                df2[["book_title", "borrow_date", "due_date", "return_date", "Status"]].rename(columns={
                    "book_title": "Book", "borrow_date": "Borrowed", "due_date": "Due", "return_date": "Returned"
                }),
                use_container_width=True,
            )
            st.caption(f"{len(hist)} borrowing record(s).")
        else:
            st.info("No borrowing history for this member.")
