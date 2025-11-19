import sqlite3
from typing import List, Optional
from .models import Task

class TodoDatabase:
    def __init__(self, db_path: str = "todo.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)) DEFAULT 0
                )
            """)

    def add_task(self, title: str, description: str = "") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
                (title, description, False)
            )
            return cursor.lastrowid

    def get_all_tasks(self) -> List[Task]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, completed FROM tasks ORDER BY id")
            rows = cursor.fetchall()
            return [Task(row[0], row[1], row[2], bool(row[3])) for row in rows]

    def toggle_task(self, task_id: int):
        with self.get_connection() as conn:
            conn.execute("UPDATE tasks SET completed = NOT completed WHERE id = ?", (task_id,))

    def delete_task(self, task_id: int):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, description, completed FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                return Task(row[0], row[1], row[2], bool(row[3]))
            return None