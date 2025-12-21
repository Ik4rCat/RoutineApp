# core/database.py

import sqlite3
from typing import List, Optional
from datetime import datetime
from .models import Task

class TodoDatabase:
    def __init__(self, db_path: str = "todo.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем существование таблицы и её структуру
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            table_exists = cursor.fetchone()

            if table_exists:
                # Получаем список колонок
                cursor.execute("PRAGMA table_info(tasks)")
                columns = [col[1] for col in cursor.fetchall()]

                # Если нет новых колонок, создаем новую таблицу с миграцией данных
                required_columns = ['category', 'status', 'priority', 'due_date', 'created_at']
                missing_columns = [col for col in required_columns if col not in columns]

                if missing_columns:
                    # Создаем новую таблицу
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS tasks_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            description TEXT DEFAULT '',
                            completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)) DEFAULT 0,
                            category TEXT DEFAULT 'Без категории',
                            status TEXT DEFAULT 'не выполнено',
                            priority TEXT DEFAULT 'нет',
                            due_date TEXT,
                            created_at TEXT
                        )
                    """)

                    # Копируем данные из старой таблицы
                    cursor.execute("""
                        INSERT INTO tasks_new (id, title, description, completed, category, status, priority, due_date, created_at)
                        SELECT id, title, description, completed,
                               'Без категории', 'не выполнено', 'нет', NULL, datetime('now', 'localtime')
                        FROM tasks
                    """)

                    # Удаляем старую таблицу и переименовываем новую
                    cursor.execute("DROP TABLE tasks")
                    cursor.execute("ALTER TABLE tasks_new RENAME TO tasks")
                    conn.commit()
            else:
                # Создаем таблицу с нуля
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT DEFAULT '',
                        completed BOOLEAN NOT NULL CHECK (completed IN (0, 1)) DEFAULT 0,
                        category TEXT DEFAULT 'Без категории',
                        status TEXT DEFAULT 'не выполнено',
                        priority TEXT DEFAULT 'нет',
                        due_date TEXT,
                        created_at TEXT
                    )
                """)
                
            # Создаем таблицу категорий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)
            
            # Добавляем стандартные категории только если таблица пустая (первый запуск)
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                standard_categories = [
                    "Работа", "Дом", "Учеба", "Спорт", 
                    "Покупки", "Здоровье", "Без категории"
                ]
                for cat in standard_categories:
                    cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
            conn.commit()

    def add_task(self, title: str, description: str = "", category: str = "Без категории",
                 priority: str = "нет", due_date: Optional[str] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Добавляем категорию в таблицу категорий, если её там нет
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
            
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                """INSERT INTO tasks (title, description, completed, category, status, priority, due_date, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (title, description, False, category, "не выполнено", priority, due_date, created_at)
            )
            return cursor.lastrowid

    def update_task(self, task_id: int, title: str, description: str, category: str,
                   priority: str, due_date: Optional[str]):
        """Обновить заголовок, описание, категорию, приоритет и срок задачи"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Добавляем категорию в таблицу категорий, если её там нет
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category,))
            
            cursor.execute(
                """UPDATE tasks
                   SET title = ?, description = ?, category = ?, priority = ?, due_date = ?
                   WHERE id = ?""",
                (title, description, category, priority, due_date, task_id)
            )

    def update_task_status(self, task_id: int, status: str):
        """Обновить статус задачи"""
        with self.get_connection() as conn:
            completed = 1 if status == "выполнено" else 0
            conn.execute(
                "UPDATE tasks SET status = ?, completed = ? WHERE id = ?",
                (status, completed, task_id)
            )

    def get_all_tasks(self) -> List[Task]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, completed, category, status, priority, due_date, created_at
                FROM tasks ORDER BY id
            """)
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

    def search_tasks(self, query: str) -> List[Task]:
        """Поиск задач по заголовку и описанию"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT id, title, description, completed, category, status, priority, due_date, created_at
                FROM tasks
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY id
            """, (search_pattern, search_pattern))
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

    def filter_tasks(self, category: Optional[str] = None, priority: Optional[str] = None,
                    status: Optional[str] = None, date_from: Optional[str] = None,
                    date_to: Optional[str] = None, sort_order: str = "ASC") -> List[Task]:
        """Фильтрация задач по категории, приоритету, статусу и дате"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT id, title, description, completed, category, status, priority, due_date, created_at
                FROM tasks WHERE 1=1
            """
            params = []

            if category and category != "Все":
                query += " AND category = ?"
                params.append(category)

            if priority and priority != "Все":
                query += " AND priority = ?"
                params.append(priority)

            if status and status != "Все":
                query += " AND status = ?"
                params.append(status)

            if date_from:
                query += " AND due_date >= ?"
                params.append(date_from)

            if date_to:
                query += " AND due_date <= ?"
                params.append(date_to)

            # Добавляем сортировку
            if sort_order.upper() == "DESC":
                query += " ORDER BY id DESC"
            else:
                query += " ORDER BY id ASC"

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

    def get_categories(self) -> List[str]:
        """Получить список всех категорий из таблицы категорий"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM categories ORDER BY name")
            return [row[0] for row in cursor.fetchall()]

    def delete_category(self, category_name: str):
        """Удалить категорию из таблицы категорий"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Удаляем категорию
            cursor.execute("DELETE FROM categories WHERE name = ?", (category_name,))
            # Обновляем задачи с этой категорией на "Без категории"
            cursor.execute("UPDATE tasks SET category = 'Без категории' WHERE category = ?", (category_name,))
            conn.commit()

    def toggle_task(self, task_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
            result = cursor.fetchone()
            if result:
                new_completed = not bool(result[0])
                new_status = "выполнено" if new_completed else "не выполнено"
                conn.execute(
                    "UPDATE tasks SET completed = ?, status = ? WHERE id = ?",
                    (new_completed, new_status, task_id)
                )

    def delete_task(self, task_id: int):
        with self.get_connection() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, completed, category, status, priority, due_date, created_at
                FROM tasks WHERE id = ?
            """, (task_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_task(row)
            return None

    def _row_to_task(self, row) -> Task:
        """Преобразовать строку БД в объект Task"""
        return Task(
            id=row[0],
            title=row[1],
            description=row[2] if row[2] else "",
            completed=bool(row[3]),
            category=row[4] if len(row) > 4 else "Без категории",
            status=row[5] if len(row) > 5 else "не выполнено",
            priority=row[6] if len(row) > 6 else "нет",
            due_date=row[7] if len(row) > 7 else None,
            created_at=row[8] if len(row) > 8 else None
        )
