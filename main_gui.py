# main_gui.py

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from core.database import TodoDatabase

Window.clearcolor = (1, 1, 1, 1)  # белый фон

class TaskItem(BoxLayout):
    def __init__(self, task, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 90
        self.task = task
        self.app = app_ref

        # === Верхняя строка: чекбокс + ТЕКСТОВЫЙ БЛОК + кнопка удаления ===
        top_row = BoxLayout(size_hint_y=None, height=40)

        # Чекбокс слева
        self.checkbox = CheckBox(
            active=task.completed,
            size_hint_x=None,
            width=40
        )
        self.checkbox.bind(on_press=self.on_checkbox_toggle)

        # Текстовый блок (заголовок + описание) — занимает всё оставшееся пространство
        text_container = BoxLayout(orientation='vertical')
        
        self.title_label = Label(
            text=task.title,
            halign='left',
            valign='middle',
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=20
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))

        # Описание — тоже слева, с небольшим отступом
        self.desc_label = Label(
            text=task.description if task.description else "",
            halign='left',
            valign='top',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=20 if task.description else 0
        )
        self.desc_label.bind(size=self.desc_label.setter('text_size'))

        text_container.add_widget(self.title_label)
        if task.description:
            text_container.add_widget(self.desc_label)

        # Кнопка удаления справа
        delete_btn = Button(
            text="Удалить",
            size_hint_x=None,
            width=100,
            on_press=self.delete_task,
            color=(1, 1, 1, 1),
            background_color=(1, 1, 1, 1)
        )

        # Собираем строку
        top_row.add_widget(self.checkbox)
        top_row.add_widget(text_container)
        top_row.add_widget(delete_btn)

        self.add_widget(top_row)

    def on_checkbox_toggle(self, checkbox):
        self.app.db.toggle_task(self.task.id)
        self.task.completed = checkbox.active

    def delete_task(self, instance):
        self.app.db.delete_task(self.task.id)
        self.app.refresh_tasks()

class TodoApp(App):
    def build(self):
        self.db = TodoDatabase()
        self.title = "To-Do List (Kivy)"

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Ввод заголовка и описания
        self.title_input = TextInput(
            hint_text="Заголовок задачи",
            multiline=False,
            size_hint_y=1,
            height=40,
            foreground_color=(0, 0, 0, 1),
            background_color=(1, 1, 1, 1)
        )
        self.desc_input = TextInput(
            hint_text="Описание (опционально)",
            multiline=True,
            size_hint_y=0.8,
            height=60,
            foreground_color=(0, 0, 0, 1),
            background_color=(1, 1, 1, 1)
        )

        add_btn = Button(
            text="Добавить задачу",
            size_hint_y=0.7,
            height=50,
            on_press=self.add_task,
            color=(1, 1, 1, 1),
            background_color=(1, 1, 1, 1)
        )

        input_box = BoxLayout(orientation='vertical', size_hint_y=None, height=120)
        input_box.add_widget(self.title_input)
        input_box.add_widget(self.desc_input)
        input_box.add_widget(add_btn)

        # Список задач
        self.task_list = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.task_list.bind(minimum_height=self.task_list.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.task_list)

        layout.add_widget(input_box)
        layout.add_widget(scroll)

        self.refresh_tasks()
        return layout

    def add_task(self, instance):
        title = self.title_input.text.strip()
        desc = self.desc_input.text.strip()
        if title:
            self.db.add_task(title, desc)
            self.title_input.text = ""
            self.desc_input.text = ""
            self.refresh_tasks()

    def refresh_tasks(self):
        self.task_list.clear_widgets()
        tasks = self.db.get_all_tasks()
        for task in tasks:
            self.task_list.add_widget(TaskItem(task=task, app_ref=self))

if __name__ == "__main__":
    TodoApp().run()