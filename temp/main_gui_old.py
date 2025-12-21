# main_gui.py - Современный интерфейс с тёмной темой

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from core.database import TodoDatabase
from core.models import Task
from typing import Optional

# Цветовая схема тёмной темы
COLORS = {
    'bg_dark': '#1a1a2e',          # Основной тёмный фон
    'bg_medium': '#16213e',         # Средний фон для панелей
    'bg_light': '#0f3460',          # Светлее для элементов ввода
    'accent': '#e94560',            # Акцентный цвет (красно-розовый)
    'accent_hover': '#ff5577',      # Акцент при наведении
    'text': '#ffffff',              # Основной текст
    'text_secondary': '#a0a0a0',    # Вторичный текст
    'success': '#00d9ff',           # Цвет успеха (голубой)
    'warning': '#ffa500',           # Предупреждение (оранжевый)
    'danger': '#ff4444',            # Опасность (красный)
    'card_bg': '#1e1e30',           # Фон карточки
    'card_hover': '#252540',        # Фон карточки при наведении
    'priority_urgent': '#ff4757',   # Срочный приоритет
    'priority_important': '#ffa502',# Важный приоритет
    'priority_normal': '#3742fa',   # Обычный приоритет
    'priority_none': '#2f3542',     # Нет приоритета
    'status_done': '#2ed573',       # Выполнено
    'status_progress': '#ffa502',   # В процессе
    'status_todo': '#5f27cd',       # Не выполнено
}
class DateTimeInput(tk.Frame):
    """Виджет для ввода даты и времени"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS['bg_medium'], **kwargs)

        # Label
        self.label = tk.Label(self, text="⏰ Срок:", bg=COLORS['bg_medium'],
                             fg=COLORS['text'], font=("Segoe UI", 10))
        self.label.pack(side=tk.LEFT, padx=(0, 10))

        # Дата
        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(self, textvariable=self.date_var, width=12,
                                   bg=COLORS['bg_light'], fg=COLORS['text'],
                                   insertbackground=COLORS['text'], relief=tk.FLAT,
                                   font=("Segoe UI", 10), bd=2)
        self.date_entry.insert(0, "ГГГГ-ММ-ДД")
        self.date_entry.bind("<FocusIn>", self._on_date_focus_in)
        self.date_entry.bind("<FocusOut>", self._on_date_focus_out)
        self.date_entry.pack(side=tk.LEFT, padx=5)

        # Время
        self.time_var = tk.StringVar()
        self.time_entry = tk.Entry(self, textvariable=self.time_var, width=8,
                                   bg=COLORS['bg_light'], fg=COLORS['text'],
                                   insertbackground=COLORS['text'], relief=tk.FLAT,
                                   font=("Segoe UI", 10), bd=2)
        self.time_entry.insert(0, "ЧЧ:ММ")
        self.time_entry.bind("<FocusIn>", self._on_time_focus_in)
        self.time_entry.bind("<FocusOut>", self._on_time_focus_out)
        self.time_entry.pack(side=tk.LEFT, padx=5)

        self._date_placeholder = True
        self._time_placeholder = True

    def _on_date_focus_in(self, event):
        if self._date_placeholder:
            self.date_entry.delete(0, tk.END)
            self._date_placeholder = False

    def _on_date_focus_out(self, event):
        if not self.date_var.get():
            self.date_entry.insert(0, "ГГГГ-ММ-ДД")
            self._date_placeholder = True

    def _on_time_focus_in(self, event):
        if self._time_placeholder:
            self.time_entry.delete(0, tk.END)
            self._time_placeholder = False

    def _on_time_focus_out(self, event):
        if not self.time_var.get():
            self.time_entry.insert(0, "ЧЧ:ММ")
            self._time_placeholder = True

    def get_datetime(self) -> Optional[str]:
        """Получить дату и время в формате строки"""
        date = self.date_var.get().strip()
        time = self.time_var.get().strip()

        if date and time and not self._date_placeholder and not self._time_placeholder:
            try:
                # Проверяем корректность формата
                datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                return f"{date} {time}"
            except:
                return None
        return None

    def set_datetime(self, datetime_str: str):
        """Установить дату и время из строки"""
        if datetime_str:
            parts = datetime_str.split()
            if len(parts) == 2:
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, parts[0])
                self._date_placeholder = False

                self.time_entry.delete(0, tk.END)
                self.time_entry.insert(0, parts[1])
                self._time_placeholder = False

    def clear(self):
        """Очистить поля ввода"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, "ГГГГ-ММ-ДД")
        self._date_placeholder = True

        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "ЧЧ:ММ")
        self._time_placeholder = True


class ModernButton(tk.Button):
    """Современная кнопка с эффектом наведения"""
    def __init__(self, parent, text, command, bg_color=None, hover_color=None,
                 fg_color=None, width=120, height=35, **kwargs):
        self.bg_color = bg_color or COLORS['accent']
        self.hover_color = hover_color or COLORS['accent_hover']
        self.fg_color = fg_color or COLORS['text']

        # Вычисляем ширину в символах (примерно)
        char_width = width // 8

        super().__init__(parent, text=text, command=command,
                        bg=self.bg_color, fg=self.fg_color,
                        font=("Arial", 10, "bold"),
                        relief=tk.FLAT, bd=0,
                        activebackground=self.hover_color,
                        activeforeground=self.fg_color,
                        cursor='hand2',
                        width=char_width,
                        **kwargs)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.configure(bg=self.hover_color)

    def _on_leave(self, e):
        self.configure(bg=self.bg_color)


class EditTaskDialog(tk.Toplevel):
    """Диалоговое окно для редактирования задачи"""
    def __init__(self, parent, task: Task, db: TodoDatabase, callback):
        super().__init__(parent)
        self.task = task
        self.db = db
        self.callback = callback

        self.title(f"✏️ Редактировать задачу #{task.id}")
        self.geometry("650x600")
        self.resizable(False, False)
        self.configure(bg=COLORS['bg_dark'])

        # Делаем окно модальным
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        # Центрируем окно
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _get_all_categories(self):
        """Получить список всех категорий"""
        standard_categories = ["Работа", "Дом", "Учеба", "Спорт", "Покупки", "Здоровье", "Без категории"]
        db_categories = self.db.get_categories()

        all_categories = standard_categories.copy()
        for cat in db_categories:
            if cat not in all_categories:
                all_categories.insert(-1, cat)

        return all_categories

    def _create_widgets(self):
        # Основной фрейм с отступами
        main_frame = tk.Frame(self, bg=COLORS['bg_dark'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        tk.Label(main_frame, text="📝 Заголовок:", font=("Segoe UI", 11, "bold"),
                bg=COLORS['bg_dark'], fg=COLORS['text']).pack(anchor=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar(value=self.task.title)
        title_entry = tk.Entry(main_frame, textvariable=self.title_var,
                              font=("Segoe UI", 11), bg=COLORS['bg_light'],
                              fg=COLORS['text'], insertbackground=COLORS['text'],
                              relief=tk.FLAT, bd=5)
        title_entry.pack(fill=tk.X, pady=(0, 15))

        # Описание
        tk.Label(main_frame, text="📄 Описание:", font=("Segoe UI", 11, "bold"),
                bg=COLORS['bg_dark'], fg=COLORS['text']).pack(anchor=tk.W, pady=(0, 5))

        desc_frame = tk.Frame(main_frame, bg=COLORS['bg_light'])
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        self.desc_text = tk.Text(desc_frame, height=5, font=("Segoe UI", 10),
                                wrap=tk.WORD, bg=COLORS['bg_light'],
                                fg=COLORS['text'], insertbackground=COLORS['text'],
                                relief=tk.FLAT, bd=5)
        self.desc_text.insert(1.0, self.task.description)
        self.desc_text.pack(fill=tk.BOTH, expand=True)

        # Категория
        cat_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        cat_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(cat_frame, text="📁 Категория:", width=15, anchor=tk.W,
                bg=COLORS['bg_dark'], fg=COLORS['text'], font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.category_var = tk.StringVar(value=self.task.category)
        all_categories = self._get_all_categories()
        category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var,
                                      values=all_categories,
                                      font=("Segoe UI", 10))
        category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Статус
        status_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        status_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(status_frame, text="📊 Статус:", width=15, anchor=tk.W,
                bg=COLORS['bg_dark'], fg=COLORS['text'], font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.status_var = tk.StringVar(value=self.task.status)
        status_combo = ttk.Combobox(status_frame, textvariable=self.status_var,
                                    values=["не выполнено", "в процессе", "выполнено"],
                                    state="readonly", font=("Segoe UI", 10))
        status_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Приоритет
        priority_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        priority_frame.pack(fill=tk.X, pady=(0, 10))
        tk.Label(priority_frame, text="⚡ Приоритет:", width=15, anchor=tk.W,
                bg=COLORS['bg_dark'], fg=COLORS['text'], font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))
        self.priority_var = tk.StringVar(value=self.task.priority)
        priority_combo = ttk.Combobox(priority_frame, textvariable=self.priority_var,
                                      values=["срочно", "важно", "обычно", "нет"],
                                      state="readonly", font=("Segoe UI", 10))
        priority_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Срок выполнения
        datetime_frame = tk.Frame(main_frame, bg=COLORS['bg_medium'], pady=10, padx=10)
        datetime_frame.pack(fill=tk.X, pady=(0, 20))
        self.datetime_input = DateTimeInput(datetime_frame)
        if self.task.due_date:
            self.datetime_input.set_datetime(self.task.due_date)
        self.datetime_input.pack(fill=tk.X)

        # Кнопки
        button_frame = tk.Frame(main_frame, bg=COLORS['bg_dark'])
        button_frame.pack(fill=tk.X)

        save_btn = ModernButton(button_frame, "✓ Сохранить", self._save_task,
                               bg_color=COLORS['success'], hover_color='#00ffaa',
                               width=200, height=40)
        save_btn.pack(side=tk.LEFT, padx=(0, 10), expand=True)

        cancel_btn = ModernButton(button_frame, "✕ Отмена", self.destroy,
                                 bg_color=COLORS['danger'], hover_color='#ff6666',
                                 width=200, height=40)
        cancel_btn.pack(side=tk.LEFT, expand=True)

    def _save_task(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Предупреждение", "Заголовок не может быть пустым!")
            return

        description = self.desc_text.get(1.0, tk.END).strip()
        category = self.category_var.get()
        priority = self.priority_var.get()
        status = self.status_var.get()
        due_date = self.datetime_input.get_datetime()

        # Обновляем задачу в БД
        if self.task.id is not None:
            self.db.update_task(self.task.id, title, description, category, priority, due_date)
            self.db.update_task_status(self.task.id, status)

        # Вызываем callback для обновления списка
        self.callback()

        self.destroy()


class TaskItem(tk.Frame):
    """Виджет для отображения одной задачи"""
    def __init__(self, parent, task: Task, db: TodoDatabase, refresh_callback, **kwargs):
        super().__init__(parent, bg=COLORS['card_bg'], **kwargs)
        self.task = task
        self.db = db
        self.refresh_callback = refresh_callback
        self.is_hovered = False

        self.configure(relief=tk.FLAT, bd=0, highlightthickness=1,
                      highlightbackground=COLORS['bg_light'])

        self._create_widgets()

        # Эффект наведения
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.configure(bg=COLORS['card_hover'], highlightbackground=COLORS['accent'])

    def _on_leave(self, e):
        self.configure(bg=COLORS['card_bg'], highlightbackground=COLORS['bg_light'])

    def _create_widgets(self):
        # Padding внутри карточки
        inner_frame = tk.Frame(self, bg=COLORS['card_bg'], padx=15, pady=15)
        inner_frame.pack(fill=tk.BOTH, expand=True)

        # Привязываем события к внутреннему фрейму тоже
        inner_frame.bind("<Enter>", self._on_enter)
        inner_frame.bind("<Leave>", self._on_leave)

        # Верхняя строка: ID и заголовок с цветным индикатором приоритета
        title_frame = tk.Frame(inner_frame, bg=COLORS['card_bg'])
        title_frame.pack(fill=tk.X, pady=(0, 8))
        title_frame.bind("<Enter>", self._on_enter)
        title_frame.bind("<Leave>", self._on_leave)

        # Цветной индикатор приоритета
        priority_color = self._get_priority_color()
        priority_indicator = tk.Canvas(title_frame, width=5, height=20, bg=priority_color,
                                      highlightthickness=0)
        priority_indicator.pack(side=tk.LEFT, padx=(0, 10))

        title_text = f"#{self.task.id}  {self.task.title}"
        if self.task.is_overdue():
            title_text += " ⚠️ ПРОСРОЧЕНО"

        title_label = tk.Label(title_frame, text=title_text, font=("Segoe UI", 12, "bold"),
                              bg=COLORS['card_bg'], fg=COLORS['text'], anchor=tk.W)
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        title_label.bind("<Enter>", self._on_enter)
        title_label.bind("<Leave>", self._on_leave)

        # Описание (если есть)
        if self.task.description:
            desc_text = self.task.description[:150] + "..." if len(self.task.description) > 150 else self.task.description
            desc_label = tk.Label(inner_frame, text=desc_text, font=("Segoe UI", 9),
                                 bg=COLORS['card_bg'], fg=COLORS['text_secondary'],
                                 anchor=tk.W, justify=tk.LEFT, wraplength=850)
            desc_label.pack(fill=tk.X, pady=(0, 10))
            desc_label.bind("<Enter>", self._on_enter)
            desc_label.bind("<Leave>", self._on_leave)

        # Информационная строка с красивыми бейджами
        info_frame = tk.Frame(inner_frame, bg=COLORS['card_bg'])
        info_frame.pack(fill=tk.X, pady=(0, 12))
        info_frame.bind("<Enter>", self._on_enter)
        info_frame.bind("<Leave>", self._on_leave)

        if self.task.category != "Без категории":
            self._create_badge(info_frame, f"📁 {self.task.category}", COLORS['priority_normal'])

        if self.task.priority != "нет":
            priority_colors = {
                "срочно": COLORS['priority_urgent'],
                "важно": COLORS['priority_important'],
                "обычно": COLORS['priority_normal'],
            }
            priority_color = priority_colors.get(self.task.priority, COLORS['priority_none'])
            self._create_badge(info_frame, f"⚡ {self.task.priority.upper()}", priority_color)

        if self.task.due_date:
            self._create_badge(info_frame, f"🕒 {self.task.due_date}", COLORS['warning'])

        # Статус бейдж
        status_colors = {
            "выполнено": COLORS['status_done'],
            "в процессе": COLORS['status_progress'],
            "не выполнено": COLORS['status_todo']
        }
        status_color = status_colors.get(self.task.status, COLORS['priority_none'])
        self._create_badge(info_frame, f"📊 {self.task.status}", status_color)

        # Строка с элементами управления
        control_frame = tk.Frame(inner_frame, bg=COLORS['card_bg'])
        control_frame.pack(fill=tk.X)
        control_frame.bind("<Enter>", self._on_enter)
        control_frame.bind("<Leave>", self._on_leave)

        # Выбор статуса
        tk.Label(control_frame, text="Изменить статус:", bg=COLORS['card_bg'],
                fg=COLORS['text_secondary'], font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))

        self.status_var = tk.StringVar(value=self.task.status)
        status_combo = ttk.Combobox(control_frame, textvariable=self.status_var,
                                    values=["не выполнено", "в процессе", "выполнено"],
                                    state="readonly", width=18, font=("Segoe UI", 9))
        status_combo.bind("<<ComboboxSelected>>", self._on_status_change)
        status_combo.pack(side=tk.LEFT, padx=(0, 15))

        # Кнопки
        edit_btn = ModernButton(control_frame, "✏️ Редактировать", self._edit_task,
                               bg_color=COLORS['success'], hover_color='#00ffaa',
                               width=130, height=32)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        delete_btn = ModernButton(control_frame, "🗑️ Удалить", self._delete_task,
                                 bg_color=COLORS['danger'], hover_color='#ff6666',
                                 width=100, height=32)
        delete_btn.pack(side=tk.LEFT)

    def _create_badge(self, parent, text, color):
        """Создать цветной бейдж"""
        badge = tk.Label(parent, text=text, bg=color, fg=COLORS['text'],
                        font=("Segoe UI", 8, "bold"), padx=10, pady=4)
        badge.pack(side=tk.LEFT, padx=(0, 8))
        badge.bind("<Enter>", self._on_enter)
        badge.bind("<Leave>", self._on_leave)

    def _get_priority_color(self) -> str:
        """Получить цвет в зависимости от приоритета"""
        if self.task.status == "выполнено":
            return COLORS['status_done']

        priority_colors = {
            "срочно": COLORS['priority_urgent'],
            "важно": COLORS['priority_important'],
            "обычно": COLORS['priority_normal'],
            "нет": COLORS['priority_none']
        }
        return priority_colors.get(self.task.priority, COLORS['priority_none'])

    def _on_status_change(self, event):
        """Обработчик изменения статуса"""
        new_status = self.status_var.get()
        if self.task.id is not None:
            self.db.update_task_status(self.task.id, new_status)
            self.refresh_callback()

    def _edit_task(self):
        """Открыть окно редактирования"""
        if self.task.id is not None:
            task = self.db.get_task_by_id(self.task.id)
            if task:
                EditTaskDialog(self.winfo_toplevel(), task, self.db, self.refresh_callback)

    def _delete_task(self):
        """Удалить задачу"""
        if self.task.id is not None:
            result = messagebox.askyesno("Подтверждение",
                                         f"Вы уверены, что хотите удалить задачу #{self.task.id}?")
            if result:
                self.db.delete_task(self.task.id)
                self.refresh_callback()


class FilterPanel(tk.Frame):
    """Панель фильтрации и поиска задач"""
    def __init__(self, parent, db: TodoDatabase, apply_callback, **kwargs):
        super().__init__(parent, bg=COLORS['bg_medium'], **kwargs)
        self.db = db
        self.apply_callback = apply_callback

        self._create_widgets()

    def _create_widgets(self):
        # Заголовок панели
        header = tk.Label(self, text="🔍 Фильтры и поиск", font=("Segoe UI", 13, "bold"),
                         bg=COLORS['bg_medium'], fg=COLORS['text'])
        header.pack(anchor=tk.W, padx=15, pady=(15, 10))

        # Padding для всего содержимого
        content_frame = tk.Frame(self, bg=COLORS['bg_medium'], padx=15, pady=10)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Строка поиска
        search_frame = tk.Frame(content_frame, bg=COLORS['bg_medium'])
        search_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(search_frame, text="🔍 Поиск:", width=12, anchor=tk.W,
                bg=COLORS['bg_medium'], fg=COLORS['text'], font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.apply_callback())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               bg=COLORS['bg_light'], fg=COLORS['text'],
                               insertbackground=COLORS['text'], relief=tk.FLAT,
                               font=("Segoe UI", 10), bd=5)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        clear_btn = ModernButton(search_frame, "✕ Очистить", self._clear_search,
                                bg_color=COLORS['bg_light'], hover_color=COLORS['accent'],
                                width=100, height=32)
        clear_btn.pack(side=tk.LEFT)

        # Фильтры - первая строка
        filter_frame1 = tk.Frame(content_frame, bg=COLORS['bg_medium'])
        filter_frame1.pack(fill=tk.X, pady=(0, 10))

        # Категория
        tk.Label(filter_frame1, text="📁 Категория:", width=12, anchor=tk.W,
                bg=COLORS['bg_medium'], fg=COLORS['text'], font=("Segoe UI", 10)).grid(
                    row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.category_var = tk.StringVar(value="Все")
        self.category_combo = ttk.Combobox(filter_frame1, textvariable=self.category_var,
                                          values=["Все"], state="readonly", width=18,
                                          font=("Segoe UI", 9))
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_callback())
        self.category_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        # Приоритет
        tk.Label(filter_frame1, text="⚡ Приоритет:", width=12, anchor=tk.W,
                bg=COLORS['bg_medium'], fg=COLORS['text'], font=("Segoe UI", 10)).grid(
                    row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.priority_var = tk.StringVar(value="Все")
        priority_combo = ttk.Combobox(filter_frame1, textvariable=self.priority_var,
                                      values=["Все", "срочно", "важно", "обычно", "нет"],
                                      state="readonly", width=18, font=("Segoe UI", 9))
        priority_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_callback())
        priority_combo.grid(row=0, column=3, sticky=tk.W)

        # Фильтры - вторая строка
        filter_frame2 = tk.Frame(content_frame, bg=COLORS['bg_medium'])
        filter_frame2.pack(fill=tk.X, pady=(0, 15))

        # Статус
        tk.Label(filter_frame2, text="📊 Статус:", width=12, anchor=tk.W,
                bg=COLORS['bg_medium'], fg=COLORS['text'], font=("Segoe UI", 10)).grid(
                    row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.status_var = tk.StringVar(value="Все")
        status_combo = ttk.Combobox(filter_frame2, textvariable=self.status_var,
                                    values=["Все", "не выполнено", "в процессе", "выполнено"],
                                    state="readonly", width=18, font=("Segoe UI", 9))
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_callback())
        status_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))

        # Сортировка
        tk.Label(filter_frame2, text="🔄 Сортировка:", width=12, anchor=tk.W,
                bg=COLORS['bg_medium'], fg=COLORS['text'], font=("Segoe UI", 10)).grid(
                    row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.sort_var = tk.StringVar(value="С начала (старые)")
        sort_combo = ttk.Combobox(filter_frame2, textvariable=self.sort_var,
                                  values=["С начала (старые)", "С конца (новые)"],
                                  state="readonly", width=20, font=("Segoe UI", 9))
        sort_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_callback())
        sort_combo.grid(row=0, column=3, sticky=tk.W)

    def update_category_values(self):
        """Обновить список категорий"""
        categories = ["Все"] + self.db.get_categories()
        current = self.category_var.get()
        self.category_combo["values"] = categories
        if current not in categories:
            self.category_var.set("Все")

    def _clear_search(self):
        """Очистить поиск"""
        self.search_var.set("")

    def _reset_filters(self):
        """Сбросить все фильтры"""
        self.search_var.set("")
        self.category_var.set("Все")
        self.priority_var.set("Все")
        self.status_var.set("Все")
        self.sort_var.set("С начала (старые)")

    def get_filters(self) -> dict:
        """Получить текущие значения фильтров"""
        return {
            "search": self.search_var.get().strip(),
            "category": None if self.category_var.get() == "Все" else self.category_var.get(),
            "priority": None if self.priority_var.get() == "Все" else self.priority_var.get(),
            "status": None if self.status_var.get() == "Все" else self.status_var.get(),
            "sort_order": "DESC" if "конца" in self.sort_var.get() else "ASC"
        }


class TodoApp:
    """Главное приложение менеджера задач с тёмной темой"""
    def __init__(self, root):
        self.root = root
        self.db = TodoDatabase()

        self.root.title("📝 Менеджер задач - Тёмная тема")
        self.root.geometry("1200x900")
        self.root.configure(bg=COLORS['bg_dark'])

        self._setup_styles()
        self._create_widgets()
        self.refresh_tasks()

    def _get_all_categories(self):
        """Получить список всех категорий (стандартные + из БД)"""
        standard_categories = ["Работа", "Дом", "Учеба", "Спорт", "Покупки", "Здоровье", "Без категории"]
        db_categories = self.db.get_categories()

        # Объединяем списки без дубликатов
        all_categories = standard_categories.copy()
        for cat in db_categories:
            if cat not in all_categories:
                all_categories.insert(-1, cat)  # Вставляем перед "Без категории"

        return all_categories

    def _setup_styles(self):
        """Настройка стилей для тёмной темы"""
        style = ttk.Style()
        style.theme_use('clam')

        # Общие стили
        style.configure(".", background=COLORS['bg_dark'], foreground=COLORS['text'])
        style.configure("TFrame", background=COLORS['bg_dark'])
        style.configure("TLabel", background=COLORS['bg_dark'], foreground=COLORS['text'], font=("Segoe UI", 10))

        # Стили для Combobox
        style.configure("TCombobox", fieldbackground=COLORS['bg_light'], background=COLORS['bg_medium'],
                       foreground=COLORS['text'], arrowcolor=COLORS['text'])
        style.map('TCombobox', fieldbackground=[('readonly', COLORS['bg_light'])],
                 selectbackground=[('readonly', COLORS['bg_light'])],
                 selectforeground=[('readonly', COLORS['text'])])

        # Стили для Scrollbar
        style.configure("Vertical.TScrollbar", background=COLORS['bg_medium'],
                       troughcolor=COLORS['bg_dark'], arrowcolor=COLORS['text'])

    def _create_widgets(self):
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=COLORS['bg_dark'], padx=15, pady=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # === ПАНЕЛЬ ДОБАВЛЕНИЯ ЗАДАЧИ ===
        add_frame = tk.LabelFrame(main_container, text="Добавить новую задачу",
                                  bg=COLORS['bg_medium'], fg=COLORS['text'],
                                  font=("Segoe UI", 12, "bold"), padx=20, pady=15)
        add_frame.pack(fill=tk.X, pady=(0, 15))

        # Заголовок
        tk.Label(add_frame, text="📝 Заголовок:", bg=COLORS['bg_medium'],
                fg=COLORS['text'], font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar()
        title_entry = tk.Entry(add_frame, textvariable=self.title_var,
                              font=("Segoe UI", 11), bg=COLORS['bg_light'],
                              fg=COLORS['text'], insertbackground=COLORS['text'],
                              relief=tk.FLAT, bd=5)
        title_entry.grid(row=0, column=1, columnspan=3, sticky=tk.EW, pady=(0, 10))

        # Описание
        tk.Label(add_frame, text="📄 Описание:", bg=COLORS['bg_medium'],
                fg=COLORS['text'], font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        desc_frame = tk.Frame(add_frame, bg=COLORS['bg_light'])
        desc_frame.grid(row=1, column=1, columnspan=3, sticky=tk.EW, pady=(0, 10))

        self.desc_text = tk.Text(desc_frame, height=3, font=("Segoe UI", 10), wrap=tk.WORD,
                                bg=COLORS['bg_light'], fg=COLORS['text'],
                                insertbackground=COLORS['text'], relief=tk.FLAT, bd=5)
        self.desc_text.pack(fill=tk.BOTH, expand=True)

        # Категория и Приоритет
        tk.Label(add_frame, text="📁 Категория:", bg=COLORS['bg_medium'],
                fg=COLORS['text'], font=("Segoe UI", 10)).grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.category_var = tk.StringVar(value="Без категории")
        self.category_combo = ttk.Combobox(add_frame, textvariable=self.category_var,
                                      values=self._get_all_categories(),
                                      width=18, font=("Segoe UI", 10))
        self.category_combo.grid(row=2, column=1, sticky=tk.W, pady=(0, 10), padx=(0, 20))

        tk.Label(add_frame, text="⚡ Приоритет:", bg=COLORS['bg_medium'],
                fg=COLORS['text'], font=("Segoe UI", 10)).grid(row=2, column=2, sticky=tk.W, pady=(0, 10))
        self.priority_var = tk.StringVar(value="нет")
        priority_combo = ttk.Combobox(add_frame, textvariable=self.priority_var,
                                      values=["срочно", "важно", "обычно", "нет"],
                                      state="readonly", width=18, font=("Segoe UI", 10))
        priority_combo.grid(row=2, column=3, sticky=tk.W, pady=(0, 10))

        # Срок выполнения
        datetime_frame = tk.Frame(add_frame, bg=COLORS['bg_medium'])
        datetime_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W, pady=(0, 15))
        self.due_date_input = DateTimeInput(datetime_frame)
        self.due_date_input.pack()

        # Кнопка добавления
        add_btn_frame = tk.Frame(add_frame, bg=COLORS['bg_medium'])
        add_btn_frame.grid(row=4, column=0, columnspan=4, sticky=tk.EW)

        add_btn = ModernButton(add_btn_frame, "✅ Добавить задачу", self._add_task,
                              bg_color=COLORS['success'], hover_color='#00ffaa',
                              width=180, height=40)
        add_btn.pack(pady=5)

        # Настройка растяжения колонок
        add_frame.columnconfigure(1, weight=1)
        add_frame.columnconfigure(3, weight=1)

        # === ПАНЕЛЬ ФИЛЬТРОВ ===
        self.filter_panel = FilterPanel(main_container, self.db, self.apply_filters)
        self.filter_panel.pack(fill=tk.X, pady=(0, 15))

        # === СПИСОК ЗАДАЧ ===
        # Фрейм для canvas и scrollbar
        tasks_container = tk.Frame(main_container, bg=COLORS['bg_dark'])
        tasks_container.pack(fill=tk.BOTH, expand=True)

        # Canvas для прокрутки
        self.canvas = tk.Canvas(tasks_container, bg=COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tasks_container, orient=tk.VERTICAL, command=self.canvas.yview)

        self.tasks_frame = tk.Frame(self.canvas, bg=COLORS['bg_dark'])
        self.tasks_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.tasks_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Привязка прокрутки колесом мыши
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux

    def _on_mousewheel(self, event):
        """Обработка прокрутки колесом мыши"""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def _add_task(self):
        """Добавить новую задачу"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Предупреждение", "Заголовок не может быть пустым!")
            return

        description = self.desc_text.get(1.0, tk.END).strip()
        category = self.category_var.get().strip()
        if not category:
            category = "Без категории"
        priority = self.priority_var.get()
        due_date = self.due_date_input.get_datetime()

        self.db.add_task(title, description, category, priority, due_date)

        # Обновляем список категорий в combobox
        self.category_combo['values'] = self._get_all_categories()

        # Очищаем поля
        self.title_var.set("")
        self.desc_text.delete(1.0, tk.END)
        self.category_var.set("Без категории")
        self.priority_var.set("нет")
        self.due_date_input.clear()

        self.refresh_tasks()

    def apply_filters(self):
        """Применить фильтры и поиск"""
        filters = self.filter_panel.get_filters()

        if filters["search"]:
            # Если есть поисковый запрос
            tasks = self.db.search_tasks(filters["search"])
        else:
            # Применяем фильтры
            tasks = self.db.filter_tasks(
                category=filters["category"],
                priority=filters["priority"],
                status=filters["status"],
                sort_order=filters["sort_order"]
            )

        self._display_tasks(tasks)

    def refresh_tasks(self):
        """Обновить список задач"""
        self.filter_panel.update_category_values()
        self.apply_filters()

    def _display_tasks(self, tasks):
        """Отобразить список задач"""
        # Очищаем текущий список
        for widget in self.tasks_frame.winfo_children():
            widget.destroy()

        # Отображаем задачи
        if not tasks:
            no_tasks_label = tk.Label(self.tasks_frame, text="📭 Задач не найдено",
                                     font=("Segoe UI", 14), fg=COLORS['text_secondary'],
                                     bg=COLORS['bg_dark'])
            no_tasks_label.pack(pady=40)
        else:
            for task in tasks:
                task_item = TaskItem(self.tasks_frame, task, self.db, self.refresh_tasks)
                task_item.pack(fill=tk.X, pady=8, padx=5)

        # Обновляем область прокрутки
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))




def main():
    """Точка входа в приложение"""
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
