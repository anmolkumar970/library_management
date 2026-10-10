"""
pages/1_Books.py — Book Catalog
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import database as db
from utils import fmt_date

st.set_page_config(page_title="Books — LibraryMS", page_icon="📖", layout="wide")
db.init_db()

st.title("📖 Book Catalog")
st.markdown("---")

# ── Search / Filter bar ───────────────────────────────────────────────────────
cats = db.get_all_categories()
cat_map = {c["name"]: c["id"] for c in cats}
cat_options = ["All"] + [c["name"] for c in cats]

col_s, col_c = st.columns([3, 1])
search = col_s.text_input("🔍 Search by title, author, or ISBN", "")
cat_filter = col_c.selectbox("Category", cat_options)

cat_id = cat_map.get(cat_filter) if cat_filter != "All" else None
books = db.get_all_books(search=search, category_id=cat_id)

# ── Book table ────────────────────────────────────────────────────────────────
if books:
    df = pd.DataFrame(books)
    df["published_date"] = df["published_date"].apply(fmt_date)
    df["availability"] = df.apply(
        lambda r: f"{r['available_copies']} / {r['total_copies']}", axis=1
    )
    display = df[["title", "author", "isbn", "category_name", "availability", "published_date"]].rename(columns={
        "title": "Title", "author": "Author", "isbn": "ISBN",
        "category_name": "Category", "availability": "Available / Total",
        "published_date": "Published",
    })
    display.index = range(1, len(display) + 1)
    st.dataframe(display, use_container_width=True)
    st.caption(f"{len(books)} book(s) found.")
else:
    st.info("No books match your search.")

st.markdown("---")

# ── Add / Edit / Delete in tabs ───────────────────────────────────────────────
tab_add, tab_edit, tab_del = st.tabs(["➕ Add Book", "✏️ Edit Book", "🗑️ Delete Book"])

# ── ADD ──────────────────────────────────────────────────────────────────────
with tab_add:
    with st.form("add_book_form"):
        st.subheader("Add a New Book")
        c1, c2 = st.columns(2)
        title   = c1.text_input("Title *")
        author  = c2.text_input("Author *")
        isbn    = c1.text_input("ISBN")
        pub_date = c2.date_input("Published Date")
        cat_sel = st.selectbox("Category", [c["name"] for c in cats])
        copies  = st.number_input("Total Copies", min_value=1, value=1)
        submitted = st.form_submit_button("Add Book")
    if submitted:
        if not title or not author:
            st.error("Title and Author are required.")
        else:
            db.add_book(isbn, title, author, cat_map[cat_sel], int(copies), str(pub_date))
            st.success(f"✅ '{title}' added successfully!")
            st.rerun()

# ── EDIT ─────────────────────────────────────────────────────────────────────
with tab_edit:
    st.subheader("Edit an Existing Book")
    if books:
        book_titles = {f"{b['title']} (ID {b['id']})": b["id"] for b in books}
        sel = st.selectbox("Select book to edit", list(book_titles.keys()), key="edit_sel")
        bid = book_titles[sel]
        book = db.get_book(bid)
        if book:
            with st.form("edit_book_form"):
                c1, c2 = st.columns(2)
                e_title  = c1.text_input("Title",  value=book["title"])
                e_author = c2.text_input("Author", value=book["author"])
                e_isbn   = c1.text_input("ISBN",   value=book["isbn"] or "")
                e_copies = c2.number_input("Total Copies", min_value=1, value=book["total_copies"])
                e_cat    = st.selectbox("Category", [c["name"] for c in cats],
                                        index=next((i for i, c in enumerate(cats) if c["id"] == book["category_id"]), 0))
                try:
                    from datetime import date
                    e_pub = st.date_input("Published Date",
                                          value=date.fromisoformat(book["published_date"]) if book["published_date"] else date.today())
                except Exception:
                    e_pub = st.date_input("Published Date")
                save = st.form_submit_button("Save Changes")
            if save:
                db.update_book(bid, e_isbn, e_title, e_author, cat_map[e_cat], int(e_copies), str(e_pub))
                st.success("✅ Book updated.")
                st.rerun()
    else:
        st.info("No books available to edit.")

# ── DELETE ────────────────────────────────────────────────────────────────────
with tab_del:
    st.subheader("Delete a Book")
    all_books = db.get_all_books()
    if all_books:
        del_map = {f"{b['title']} (ID {b['id']})": b["id"] for b in all_books}
        del_sel = st.selectbox("Select book to delete", list(del_map.keys()), key="del_sel")
        if st.button("🗑️ Delete", type="primary"):
            db.delete_book(del_map[del_sel])
            st.success("Book deleted.")
            st.rerun()
    else:
        st.info("No books to delete.")
