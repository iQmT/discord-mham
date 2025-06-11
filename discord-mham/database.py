import sqlite3
import os

DB_NAME = "database.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                approved_by INTEGER,
                category TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def insert_approval(user_id: int, status: str, approved_by: int, category: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO approvals (user_id, status, approved_by, category)
            VALUES (?, ?, ?, ?)
        """, (user_id, status, approved_by, category))
        conn.commit()

def get_all_approvals_grouped():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, category, COUNT(*) as count
            FROM approvals
            WHERE status = 'accepted'
            GROUP BY user_id, category
        """)
        return cursor.fetchall()

def delete_all_approvals():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM approvals")
        conn.commit()

def get_user_approvals(user_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM approvals
            WHERE user_id = ? AND status = 'accepted'
            GROUP BY category
        """, (user_id,))
        return cursor.fetchall()


def delete_user_category(user_id: int, category: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM approvals WHERE user_id = ? AND category = ?", (user_id, category))
        conn.commit()

def add_multiple_approvals(user_id: int, count: int, approved_by: int, category: str):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        for _ in range(count):
            cursor.execute("""
                INSERT INTO approvals (user_id, status, approved_by, category)
                VALUES (?, 'accepted', ?, ?)
            """, (user_id, approved_by, category))
        conn.commit()

def get_logs(limit=20):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_id, approved_by, category, status, timestamp
            FROM approvals
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
