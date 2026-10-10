"""
pages/5_Trends.py — Borrowing Trends Dashboard
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

import database as db

st.set_page_config(page_title="Trends — LibraryMS", page_icon="📊", layout="wide")
db.init_db()
db.refresh_overdue()

PALETTE = sns.color_palette("muted")
sns.set_theme(style="whitegrid", palette="muted")

st.title("📊 Borrowing Trends Dashboard")
st.markdown("---")

# ── KPI row ───────────────────────────────────────────────────────────────────
summary = db.dashboard_summary()
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Total Copies",   summary["total_books"])
c2.metric("✅ Available",       summary["available"])
c3.metric("👤 Members",         summary["total_members"])
c4.metric("🔵 Active Borrows",  summary["active_borrows"])
c5.metric("🔴 Overdue",         summary["overdue"])

st.markdown("---")

# ── Row 1: Monthly trend  +  Borrow status donut ─────────────────────────────
row1_left, row1_right = st.columns([2, 1])

with row1_left:
    st.subheader("📈 Monthly Borrowings")
    monthly = db.trend_monthly_borrowings()
    if monthly:
        df_m = pd.DataFrame(monthly)
        fig, ax = plt.subplots(figsize=(8, 3.5))
        ax.plot(df_m["month"], df_m["count"], marker="o", linewidth=2,
                color=PALETTE[0], markerfacecolor="white", markeredgewidth=2)
        ax.fill_between(df_m["month"], df_m["count"], alpha=0.15, color=PALETTE[0])
        ax.set_xlabel("Month", fontsize=10)
        ax.set_ylabel("Borrowings", fontsize=10)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        step = max(1, len(df_m) // 8)
        ax.set_xticks(df_m["month"][::step])
        ax.tick_params(axis="x", rotation=35, labelsize=8)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No borrowing data yet.")

with row1_right:
    st.subheader("🔵 Borrowing Status")
    status_data = db.trend_status_summary()
    if status_data:
        labels = list(status_data.keys())
        sizes  = list(status_data.values())
        colour_map = {"Returned": "#4ade80", "Borrowed": "#60a5fa", "Overdue": "#f87171"}
        colours = [colour_map.get(l, "#d1d5db") for l in labels]
        fig2, ax2 = plt.subplots(figsize=(4, 3.5))
        wedges, texts, autotexts = ax2.pie(
            sizes, labels=labels, colors=colours,
            autopct="%1.0f%%", startangle=90,
            wedgeprops=dict(width=0.55),
        )
        for at in autotexts:
            at.set_fontsize(9)
        ax2.set_title("All-time distribution", fontsize=9, pad=4)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

st.markdown("---")

# ── Row 2: Top books  +  Category breakdown ───────────────────────────────────
row2_left, row2_right = st.columns(2)

with row2_left:
    st.subheader("🔥 Top 10 Most Borrowed Books")
    top_books = db.trend_top_books(10)
    if top_books:
        df_tb = pd.DataFrame(top_books)
        df_tb = df_tb.sort_values("borrow_count")
        fig3, ax3 = plt.subplots(figsize=(6, 5))
        bars = ax3.barh(df_tb["title"], df_tb["borrow_count"],
                        color=PALETTE[1], edgecolor="white", height=0.6)
        ax3.bar_label(bars, padding=3, fontsize=8)
        ax3.set_xlabel("Times Borrowed", fontsize=9)
        ax3.tick_params(axis="y", labelsize=8)
        ax3.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        fig3.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

with row2_right:
    st.subheader("🏷️ Borrowings by Category")
    cat_data = db.trend_by_category()
    if cat_data:
        df_cat = pd.DataFrame(cat_data).sort_values("borrow_count")
        fig4, ax4 = plt.subplots(figsize=(6, 5))
        bars2 = ax4.barh(df_cat["category"], df_cat["borrow_count"],
                         color=PALETTE[2], edgecolor="white", height=0.6)
        ax4.bar_label(bars2, padding=3, fontsize=9)
        ax4.set_xlabel("Times Borrowed", fontsize=9)
        ax4.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax4.tick_params(axis="y", labelsize=9)
        fig4.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

st.markdown("---")

# ── Row 3: Top Members  +  Available vs Borrowed per category ─────────────────
row3_left, row3_right = st.columns(2)

with row3_left:
    st.subheader("🏆 Most Active Members")
    top_mem = db.trend_top_members(10)
    if top_mem:
        df_mem = pd.DataFrame(top_mem)
        df_mem.index = range(1, len(df_mem) + 1)
        df_mem.columns = ["Member", "Borrowings"]
        st.dataframe(df_mem, use_container_width=True)

with row3_right:
    st.subheader("📦 Book Availability by Category")
    cats  = db.get_all_categories()
    if cats:
        avail_rows = []
        for c in cats:
            books = db.get_all_books(category_id=c["id"])
            total     = sum(b["total_copies"] for b in books)
            available = sum(b["available_copies"] for b in books)
            borrowed  = total - available
            avail_rows.append({"Category": c["name"], "Available": available, "Borrowed": borrowed})
        df_av = pd.DataFrame(avail_rows).set_index("Category")
        df_av = df_av[df_av["Available"] + df_av["Borrowed"] > 0]
        fig5, ax5 = plt.subplots(figsize=(6, 4))
        df_av.plot(kind="barh", stacked=True, ax=ax5,
                   color=["#4ade80", "#f87171"], edgecolor="white")
        ax5.set_xlabel("Copies", fontsize=9)
        ax5.tick_params(axis="y", labelsize=8)
        ax5.legend(loc="lower right", fontsize=8)
        ax5.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        fig5.tight_layout()
        st.pyplot(fig5)
        plt.close(fig5)

st.markdown("---")
st.caption("📊 Trends refresh each time the page loads.")
