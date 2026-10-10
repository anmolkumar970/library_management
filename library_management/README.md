# ?? Library Management System

A full-featured **Library Management System** built with Python and Streamlit. Manage books, categories, members, and book circulation — with a live borrowing trends dashboard.

---

## ?? Features

| Module | Description |
|---|---|
| ?? **Books** | Add, edit, delete, and search books by title, author, ISBN, or category |
| ??? **Categories** | Manage genres/subjects and browse books per category |
| ?? **Members** | Register members, manage status (Active/Suspended), view borrowing history |
| ?? **Circulation** | Issue books to members, process returns, detect overdue loans |
| ?? **Trends Dashboard** | Visual analytics — monthly trends, top books, category breakdown, member leaderboard |

---

## ??? Screenshots

### Home Dashboard
- 5 live KPI metrics (Total Copies, Available, Members, Active Borrows, Overdue)
- Top 5 most borrowed books
- Active & overdue borrowings table

### Trends Dashboard
- ?? Monthly borrowing line chart
- ?? Borrowing status donut chart (Returned / Borrowed / Overdue)
- ?? Top 10 most borrowed books (horizontal bar)
- ??? Borrowings by category (horizontal bar)
- ?? Book availability per category (stacked bar)
- ?? Most active members leaderboard

---

## ??? Project Structure

`
library_management/
+-- app.py                  # Streamlit entry point & home dashboard
+-- database.py             # SQLite schema, seed data, all CRUD & analytics queries
+-- utils.py                # Shared helpers (date formatting, overdue calc, badges)
+-- requirements.txt        # Python dependencies
+-- pages/
    +-- 1_Books.py          # Book catalog — search, filter, add/edit/delete
    +-- 2_Categories.py     # Category CRUD + browse books by category
    +-- 3_Members.py        # Member registration, edit, borrowing history
    +-- 4_Circulation.py    # Issue & return books, overdue alerts, full log
    +-- 5_Trends.py         # Borrowing trends analytics dashboard
`

---

## ??? Database Schema

`
categories     — id, name, description
books          — id, isbn, title, author, category_id, total_copies, available_copies, published_date
members        — id, name, email, phone, join_date, status
borrowings     — id, book_id, member_id, borrow_date, due_date, return_date, status
`

The SQLite database (library.db) is created automatically on first run with sample seed data:
- **8 categories** (Fiction, Science, Technology, History, Philosophy, Children, Self-Help, Reference)
- **23 books** (105 total copies)
- **10 members**
- **30 borrowing records** (active, returned, and overdue)

---

## ?? Installation & Setup

### Prerequisites
- Python 3.9+
- pip

### 1. Clone the repository
`ash
git clone https://github.com/anmolkumar970/library_management.git
cd library_management
`

### 2. Install dependencies
`ash
pip install -r library_management/requirements.txt
`

### 3. Run the app
`ash
streamlit run library_management/app.py
`

The app will open automatically at **http://localhost:8501**

---

## ?? Dependencies

| Package | Purpose |
|---|---|
| streamlit | Web UI framework |
| pandas | Data manipulation & table display |
| matplotlib | Charts and plots |
| seaborn | Chart styling |
| sqlite3 | Database (built into Python) |

---

## ?? Usage Guide

### Issuing a Book
1. Go to **?? Circulation** ? **?? Issue Book** tab
2. Select an active member and an available book
3. Set borrow date and due date ? click **Issue Book**

### Returning a Book
1. Go to **?? Circulation** ? **?? Return Book** tab
2. Select the borrowing record ? set return date ? click **Process Return**

### Viewing Trends
1. Go to **?? Trends** page
2. All charts update automatically based on live database data

---

## ??? Tech Stack

- **Frontend:** Streamlit (multi-page app)
- **Backend:** Python 3
- **Database:** SQLite (via built-in sqlite3)
- **Data Layer:** Pandas
- **Charts:** Matplotlib + Seaborn

---

## ?? License

MIT License — free to use, modify, and distribute.

---

*Built with Python & Streamlit*
