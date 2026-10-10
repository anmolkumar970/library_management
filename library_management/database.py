"""
database.py — SQLite layer for the Library Management System
=============================================================
All schema creation, seed data, and CRUD helpers live here.
"""

import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "library.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                description TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS books (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn             TEXT    UNIQUE,
                title            TEXT    NOT NULL,
                author           TEXT    NOT NULL,
                category_id      INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                total_copies     INTEGER NOT NULL DEFAULT 1,
                available_copies INTEGER NOT NULL DEFAULT 1,
                published_date   TEXT
            );

            CREATE TABLE IF NOT EXISTS members (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                email     TEXT    UNIQUE,
                phone     TEXT,
                join_date TEXT    NOT NULL,
                status    TEXT    NOT NULL DEFAULT 'Active'
            );

            CREATE TABLE IF NOT EXISTS borrowings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id     INTEGER NOT NULL REFERENCES books(id),
                member_id   INTEGER NOT NULL REFERENCES members(id),
                borrow_date TEXT    NOT NULL,
                due_date    TEXT    NOT NULL,
                return_date TEXT,
                status      TEXT    NOT NULL DEFAULT 'Borrowed'
            );
        """)
        _seed_if_empty(conn)


def _seed_if_empty(conn):
    if conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0] > 0:
        return

    # ── Categories ──────────────────────────────────────────────────────────
    categories = [
        ("Fiction",       "Novels, short stories, and literary works"),
        ("Science",       "Natural sciences, physics, biology, chemistry"),
        ("Technology",    "Computing, engineering, and applied sciences"),
        ("History",       "World history, biographies, and chronicles"),
        ("Philosophy",    "Ethics, logic, metaphysics, and social theory"),
        ("Children",      "Picture books, early readers, and middle grade"),
        ("Self-Help",     "Personal development and motivational works"),
        ("Reference",     "Encyclopaedias, dictionaries, and atlases"),
    ]
    conn.executemany("INSERT INTO categories (name, description) VALUES (?,?)", categories)

    cat = {r["name"]: r["id"] for r in conn.execute("SELECT id, name FROM categories")}

    # ── Books ────────────────────────────────────────────────────────────────
    books = [
        ("978-0-7432-7356-5", "The Great Gatsby",               "F. Scott Fitzgerald", cat["Fiction"],    4, 3, "1925-04-10"),
        ("978-0-06-112008-4", "To Kill a Mockingbird",          "Harper Lee",          cat["Fiction"],    5, 4, "1960-07-11"),
        ("978-0-14-028329-7", "1984",                           "George Orwell",       cat["Fiction"],    6, 5, "1949-06-08"),
        ("978-0-7432-7357-2", "Brave New World",                "Aldous Huxley",       cat["Fiction"],    3, 2, "1932-01-01"),
        ("978-0-316-76948-0", "The Catcher in the Rye",         "J.D. Salinger",       cat["Fiction"],    4, 4, "1951-07-16"),
        ("978-0-385-33348-1", "A Brief History of Time",        "Stephen Hawking",     cat["Science"],    5, 3, "1988-04-01"),
        ("978-0-393-31777-8", "The Selfish Gene",               "Richard Dawkins",     cat["Science"],    3, 3, "1976-05-01"),
        ("978-0-385-49081-8", "Cosmos",                        "Carl Sagan",          cat["Science"],    4, 2, "1980-09-01"),
        ("978-0-7432-7358-9", "The Double Helix",               "James D. Watson",     cat["Science"],    2, 2, "1968-01-01"),
        ("978-0-13-110362-7", "The C Programming Language",     "Kernighan & Ritchie", cat["Technology"], 6, 5, "1978-01-01"),
        ("978-0-13-468599-1", "Clean Code",                    "Robert C. Martin",    cat["Technology"], 5, 4, "2008-08-01"),
        ("978-0-596-51774-8", "Learning Python",                "Mark Lutz",           cat["Technology"], 4, 3, "2013-06-01"),
        ("978-0-13-235088-4", "The Pragmatic Programmer",       "Hunt & Thomas",       cat["Technology"], 3, 3, "1999-10-20"),
        ("978-0-14-303943-3", "Sapiens",                        "Yuval Noah Harari",   cat["History"],    7, 5, "2011-01-01"),
        ("978-0-06-093546-9", "Guns, Germs, and Steel",         "Jared Diamond",       cat["History"],    4, 3, "1997-03-01"),
        ("978-0-14-028381-5", "The Art of War",                 "Sun Tzu",             cat["History"],    5, 5, "500-01-01"),
        ("978-0-14-044913-6", "Meditations",                    "Marcus Aurelius",     cat["Philosophy"], 4, 3, "180-01-01"),
        ("978-0-14-044914-3", "The Republic",                   "Plato",               cat["Philosophy"], 3, 2, "-380-01-01"),
        ("978-0-06-196436-5", "The Very Hungry Caterpillar",    "Eric Carle",          cat["Children"],   8, 7, "1969-03-20"),
        ("978-0-06-440055-8", "Charlotte's Web",                "E.B. White",          cat["Children"],   6, 5, "1952-10-15"),
        ("978-0-7432-7359-6", "Atomic Habits",                  "James Clear",         cat["Self-Help"],  7, 4, "2018-10-16"),
        ("978-0-7432-7360-2", "The 7 Habits of Highly Effective People", "Stephen Covey", cat["Self-Help"], 5, 3, "1989-08-15"),
        ("978-0-521-43723-0", "Oxford English Dictionary",      "OUP",                 cat["Reference"],  2, 2, "1884-01-01"),
    ]
    conn.executemany(
        "INSERT INTO books (isbn, title, author, category_id, total_copies, available_copies, published_date) VALUES (?,?,?,?,?,?,?)",
        books,
    )

    # ── Members ──────────────────────────────────────────────────────────────
    members = [
        ("Alice Mwangi",    "alice@example.com",   "+254 700 111 001", "2022-01-15", "Active"),
        ("Brian Otieno",    "brian@example.com",   "+254 700 111 002", "2022-03-20", "Active"),
        ("Carol Njeri",     "carol@example.com",   "+254 700 111 003", "2022-05-10", "Active"),
        ("David Kimani",    "david@example.com",   "+254 700 111 004", "2022-07-01", "Active"),
        ("Emily Wanjiku",   "emily@example.com",   "+254 700 111 005", "2022-09-14", "Active"),
        ("Felix Omondi",    "felix@example.com",   "+254 700 111 006", "2023-01-05", "Active"),
        ("Grace Achieng",   "grace@example.com",   "+254 700 111 007", "2023-03-22", "Active"),
        ("Henry Mutua",     "henry@example.com",   "+254 700 111 008", "2023-06-18", "Suspended"),
        ("Irene Kamau",     "irene@example.com",   "+254 700 111 009", "2023-08-30", "Active"),
        ("James Ndung'u",   "james@example.com",   "+254 700 111 010", "2024-01-10", "Active"),
    ]
    conn.executemany(
        "INSERT INTO members (name, email, phone, join_date, status) VALUES (?,?,?,?,?)",
        members,
    )

    # ── Borrowings (historical + active) ─────────────────────────────────────
    today = date.today()

    def d(days_ago):
        return str(today - timedelta(days=days_ago))

    def due(days_ago, loan=14):
        b = today - timedelta(days=days_ago)
        return str(b + timedelta(days=loan))

    borrowings = [
        # book_id, member_id, borrow_date, due_date, return_date, status
        (1,  1,  d(120), due(120), d(106), "Returned"),
        (2,  2,  d(115), due(115), d(101), "Returned"),
        (3,  3,  d(110), due(110), d(96),  "Returned"),
        (14, 4,  d(105), due(105), d(91),  "Returned"),
        (10, 5,  d(100), due(100), d(86),  "Returned"),
        (21, 6,  d(95),  due(95),  d(81),  "Returned"),
        (6,  7,  d(90),  due(90),  d(76),  "Returned"),
        (15, 8,  d(85),  due(85),  d(71),  "Returned"),
        (19, 9,  d(80),  due(80),  d(66),  "Returned"),
        (4,  10, d(75),  due(75),  d(61),  "Returned"),
        (11, 1,  d(70),  due(70),  d(56),  "Returned"),
        (7,  2,  d(65),  due(65),  d(51),  "Returned"),
        (16, 3,  d(60),  due(60),  d(46),  "Returned"),
        (20, 4,  d(55),  due(55),  d(41),  "Returned"),
        (5,  5,  d(50),  due(50),  d(36),  "Returned"),
        (13, 6,  d(45),  due(45),  d(31),  "Returned"),
        (8,  7,  d(40),  due(40),  d(26),  "Returned"),
        (22, 8,  d(35),  due(35),  d(21),  "Returned"),
        (17, 9,  d(30),  due(30),  d(16),  "Returned"),
        (3,  10, d(28),  due(28),  d(14),  "Returned"),
        (14, 1,  d(25),  due(25),  d(11),  "Returned"),
        (21, 2,  d(22),  due(22),  d(8),   "Returned"),
        (10, 3,  d(20),  due(20),  d(6),   "Returned"),
        # active / overdue
        (1,  4,  d(10),  due(10),  None,   "Borrowed"),
        (6,  5,  d(12),  due(12),  None,   "Borrowed"),
        (14, 6,  d(8),   due(8),   None,   "Borrowed"),
        (11, 7,  d(20),  due(20),  None,   "Overdue"),   # past due
        (3,  8,  d(25),  due(25),  None,   "Overdue"),   # past due
        (2,  9,  d(5),   due(5),   None,   "Borrowed"),
        (21, 10, d(3),   due(3),   None,   "Borrowed"),
    ]
    conn.executemany(
        "INSERT INTO borrowings (book_id, member_id, borrow_date, due_date, return_date, status) VALUES (?,?,?,?,?,?)",
        borrowings,
    )


# ---------------------------------------------------------------------------
# Category helpers
# ---------------------------------------------------------------------------

def get_all_categories():
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM categories ORDER BY name")]

def add_category(name, description=""):
    with get_conn() as conn:
        conn.execute("INSERT INTO categories (name, description) VALUES (?,?)", (name, description))

def update_category(cat_id, name, description):
    with get_conn() as conn:
        conn.execute("UPDATE categories SET name=?, description=? WHERE id=?", (name, description, cat_id))

def delete_category(cat_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))


# ---------------------------------------------------------------------------
# Book helpers
# ---------------------------------------------------------------------------

def get_all_books(search="", category_id=None):
    sql = """
        SELECT b.*, c.name AS category_name
        FROM books b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE (b.title LIKE ? OR b.author LIKE ? OR b.isbn LIKE ?)
    """
    params = [f"%{search}%", f"%{search}%", f"%{search}%"]
    if category_id:
        sql += " AND b.category_id = ?"
        params.append(category_id)
    sql += " ORDER BY b.title"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, params)]

def get_book(book_id):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM books WHERE id=?", (book_id,)).fetchone()
        return dict(r) if r else None

def add_book(isbn, title, author, category_id, total_copies, published_date):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO books (isbn, title, author, category_id, total_copies, available_copies, published_date) VALUES (?,?,?,?,?,?,?)",
            (isbn, title, author, category_id, total_copies, total_copies, published_date),
        )

def update_book(book_id, isbn, title, author, category_id, total_copies, published_date):
    with get_conn() as conn:
        conn.execute(
            "UPDATE books SET isbn=?, title=?, author=?, category_id=?, total_copies=?, published_date=? WHERE id=?",
            (isbn, title, author, category_id, total_copies, published_date, book_id),
        )

def delete_book(book_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM books WHERE id=?", (book_id,))


# ---------------------------------------------------------------------------
# Member helpers
# ---------------------------------------------------------------------------

def get_all_members(search="", status=None):
    sql = "SELECT * FROM members WHERE (name LIKE ? OR email LIKE ?)"
    params = [f"%{search}%", f"%{search}%"]
    if status:
        sql += " AND status=?"
        params.append(status)
    sql += " ORDER BY name"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, params)]

def get_member(member_id):
    with get_conn() as conn:
        r = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
        return dict(r) if r else None

def add_member(name, email, phone, join_date, status="Active"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO members (name, email, phone, join_date, status) VALUES (?,?,?,?,?)",
            (name, email, phone, join_date, status),
        )

def update_member(member_id, name, email, phone, status):
    with get_conn() as conn:
        conn.execute(
            "UPDATE members SET name=?, email=?, phone=?, status=? WHERE id=?",
            (name, email, phone, status, member_id),
        )

def delete_member(member_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))


# ---------------------------------------------------------------------------
# Borrowing helpers
# ---------------------------------------------------------------------------

def get_active_borrowings():
    sql = """
        SELECT bw.*, b.title AS book_title, m.name AS member_name
        FROM borrowings bw
        JOIN books b ON bw.book_id = b.id
        JOIN members m ON bw.member_id = m.id
        WHERE bw.status IN ('Borrowed','Overdue')
        ORDER BY bw.due_date
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql)]

def get_all_borrowings():
    sql = """
        SELECT bw.*, b.title AS book_title, m.name AS member_name
        FROM borrowings bw
        JOIN books b ON bw.book_id = b.id
        JOIN members m ON bw.member_id = m.id
        ORDER BY bw.borrow_date DESC
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql)]

def get_member_borrowings(member_id):
    sql = """
        SELECT bw.*, b.title AS book_title
        FROM borrowings bw
        JOIN books b ON bw.book_id = b.id
        WHERE bw.member_id = ?
        ORDER BY bw.borrow_date DESC
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, (member_id,))]

def borrow_book(book_id, member_id, borrow_date, due_date):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO borrowings (book_id, member_id, borrow_date, due_date, status) VALUES (?,?,?,?,'Borrowed')",
            (book_id, member_id, borrow_date, due_date),
        )
        conn.execute(
            "UPDATE books SET available_copies = available_copies - 1 WHERE id=?",
            (book_id,),
        )

def return_book(borrowing_id, return_date):
    with get_conn() as conn:
        row = conn.execute("SELECT book_id FROM borrowings WHERE id=?", (borrowing_id,)).fetchone()
        if row:
            conn.execute(
                "UPDATE borrowings SET return_date=?, status='Returned' WHERE id=?",
                (return_date, borrowing_id),
            )
            conn.execute(
                "UPDATE books SET available_copies = available_copies + 1 WHERE id=?",
                (row["book_id"],),
            )

def refresh_overdue():
    today = str(date.today())
    with get_conn() as conn:
        conn.execute(
            "UPDATE borrowings SET status='Overdue' WHERE status='Borrowed' AND due_date < ?",
            (today,),
        )

# ---------------------------------------------------------------------------
# Trend / analytics queries
# ---------------------------------------------------------------------------

def trend_monthly_borrowings():
    sql = """
        SELECT strftime('%Y-%m', borrow_date) AS month, COUNT(*) AS count
        FROM borrowings
        GROUP BY month ORDER BY month
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql)]

def trend_top_books(limit=10):
    sql = """
        SELECT b.title, b.author, COUNT(*) AS borrow_count
        FROM borrowings bw JOIN books b ON bw.book_id = b.id
        GROUP BY bw.book_id ORDER BY borrow_count DESC LIMIT ?
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, (limit,))]

def trend_by_category():
    sql = """
        SELECT c.name AS category, COUNT(*) AS borrow_count
        FROM borrowings bw
        JOIN books b ON bw.book_id = b.id
        JOIN categories c ON b.category_id = c.id
        GROUP BY c.id ORDER BY borrow_count DESC
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql)]

def trend_top_members(limit=10):
    sql = """
        SELECT m.name, COUNT(*) AS borrow_count
        FROM borrowings bw JOIN members m ON bw.member_id = m.id
        GROUP BY bw.member_id ORDER BY borrow_count DESC LIMIT ?
    """
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(sql, (limit,))]

def trend_status_summary():
    sql = "SELECT status, COUNT(*) AS count FROM borrowings GROUP BY status"
    with get_conn() as conn:
        return {r["status"]: r["count"] for r in conn.execute(sql)}

def dashboard_summary():
    with get_conn() as conn:
        total_books     = conn.execute("SELECT SUM(total_copies) FROM books").fetchone()[0] or 0
        available       = conn.execute("SELECT SUM(available_copies) FROM books").fetchone()[0] or 0
        total_members   = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0] or 0
        active_borrows  = conn.execute("SELECT COUNT(*) FROM borrowings WHERE status='Borrowed'").fetchone()[0] or 0
        overdue         = conn.execute("SELECT COUNT(*) FROM borrowings WHERE status='Overdue'").fetchone()[0] or 0
    return {
        "total_books":    total_books,
        "available":      available,
        "total_members":  total_members,
        "active_borrows": active_borrows,
        "overdue":        overdue,
    }
