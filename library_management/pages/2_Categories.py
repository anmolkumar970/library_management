"""
pages/2_Categories.py — Category Management
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import database as db

st.set_page_config(page_title="Categories — LibraryMS", page_icon="🏷️", layout="wide")
db.init_db()

st.title("🏷️ Categories")
st.markdown("---")

cats = db.get_all_categories()

# ── Category overview table ───────────────────────────────────────────────────
if cats:
    # Enrich with book count
    rows = []
    for c in cats:
        books = db.get_all_books(category_id=c["id"])
        rows.append({
            "ID": c["id"],
            "Name": c["name"],
            "Description": c["description"],
            "Books": len(books),
        })
    df = pd.DataFrame(rows)
    df.index = range(1, len(df) + 1)
    st.dataframe(df, use_container_width=True)
    st.caption(f"{len(cats)} categories.")
else:
    st.info("No categories yet.")

st.markdown("---")

tab_add, tab_edit, tab_del, tab_browse = st.tabs([
    "➕ Add", "✏️ Edit", "🗑️ Delete", "📚 Browse Books by Category"
])

# ── ADD ──────────────────────────────────────────────────────────────────────
with tab_add:
    with st.form("add_cat_form"):
        st.subheader("Add Category")
        name = st.text_input("Name *")
        desc = st.text_area("Description")
        ok   = st.form_submit_button("Add")
    if ok:
        if not name:
            st.error("Name is required.")
        else:
            try:
                db.add_category(name.strip(), desc.strip())
                st.success(f"✅ Category '{name}' added.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ── EDIT ─────────────────────────────────────────────────────────────────────
with tab_edit:
    st.subheader("Edit Category")
    if cats:
        sel_map = {c["name"]: c["id"] for c in cats}
        sel     = st.selectbox("Select category", list(sel_map.keys()), key="edit_cat_sel")
        cat     = next(c for c in cats if c["name"] == sel)
        with st.form("edit_cat_form"):
            new_name = st.text_input("Name", value=cat["name"])
            new_desc = st.text_area("Description", value=cat["description"])
            save     = st.form_submit_button("Save")
        if save:
            db.update_category(cat["id"], new_name.strip(), new_desc.strip())
            st.success("✅ Category updated.")
            st.rerun()

# ── DELETE ────────────────────────────────────────────────────────────────────
with tab_del:
    st.subheader("Delete Category")
    if cats:
        del_map = {c["name"]: c["id"] for c in cats}
        del_sel = st.selectbox("Select category", list(del_map.keys()), key="del_cat_sel")
        st.warning("Deleting a category will set its books' category to NULL.")
        if st.button("🗑️ Delete Category", type="primary"):
            db.delete_category(del_map[del_sel])
            st.success("Category deleted.")
            st.rerun()

# ── BROWSE ────────────────────────────────────────────────────────────────────
with tab_browse:
    st.subheader("Browse Books by Category")
    if cats:
        browse_sel = st.selectbox("Category", [c["name"] for c in cats], key="browse_cat")
        cat_id     = next(c["id"] for c in cats if c["name"] == browse_sel)
        books      = db.get_all_books(category_id=cat_id)
        if books:
            df2 = pd.DataFrame(books)[["title", "author", "isbn", "available_copies", "total_copies"]]
            df2.columns = ["Title", "Author", "ISBN", "Available", "Total"]
            df2.index = range(1, len(df2) + 1)
            st.dataframe(df2, use_container_width=True)
            st.caption(f"{len(books)} book(s) in '{browse_sel}'.")
        else:
            st.info(f"No books in '{browse_sel}'.")
