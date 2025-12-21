# core/models.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Task:
    id: Optional[int]
    title: str
    description: str = ""
    completed: bool = False
    category: str = "Без категории"  # работа, дом, учеба, и т.д.
    status: str = "не выполнено"  # выполнено, в процессе, не выполнено
    priority: str = "нет"  # срочно, важно, обычно, нет
    due_date: Optional[str] = None  # дата и время выполнения в формате "YYYY-MM-DD HH:MM"
    created_at: Optional[str] = None  # дата создания

    def get_priority_color(self) -> tuple:
        """Возвращает цвет фона в зависимости от приоритета"""
        if self.status == "выполнено":
            return (0.95, 0.95, 0.95, 1)  # серый для выполненных

        priority_colors = {
            "срочно": (1, 0.3, 0.3, 1),      # красный
            "важно": (1, 0.65, 0.3, 1),      # оранжевый
            "обычно": (0.5, 0.9, 0.5, 1),    # зелёный
            "нет": (1, 1, 1, 1)               # белый
        }
        return priority_colors.get(self.priority, (1, 1, 1, 1))

    def is_overdue(self) -> bool:
        """Проверяет, просрочена ли задача"""
        if not self.due_date or self.status == "выполнено":
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d %H:%M")
            return datetime.now() > due
        except:
            return False
