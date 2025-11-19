from core.database import TodoDatabase
from core.models import Task

def print_task(task: Task):
    status = "✓" if task.completed else "○"
    desc = f"\n      {task.description}" if task.description else ""
    print(f"{task.id}. [{status}] {task.title}{desc}")

def show_all_tasks(db: TodoDatabase):
    tasks = db.get_all_tasks()
    if not tasks:
        print("\nСписок задач пуст.\n")
    else:
        print("\n=== Ваши задачи ===")
        for task in tasks:
            print_task(task)
        print()

def add_task_interactive(db: TodoDatabase):
    print("\n--- Добавление новой задачи ---")
    title = input("Заголовок: ").strip()
    if not title:
        print("Ошибка: заголовок обязателен.\n")
        return
    description = input("Описание (опционально): ").strip()
    task_id = db.add_task(title, description)
    print(f"✅ Задача добавлена (ID: {task_id})\n")

def toggle_task_status(db: TodoDatabase):
    show_all_tasks(db)
    try:
        task_id = int(input("ID задачи для переключения статуса: "))
    except ValueError:
        print("Ошибка: ID должен быть числом.\n")
        return

    task = db.get_task_by_id(task_id)
    if not task:
        print(f"Ошибка: задача с ID {task_id} не найдена.\n")
        return

    db.toggle_task(task_id)
    new_status = "выполнена" if not task.completed else "не выполнена"
    print(f"✅ Статус задачи '{task.title}' обновлён: {new_status}.\n")

def delete_task_interactive(db: TodoDatabase):
    show_all_tasks(db)
    try:
        task_id = int(input("ID задачи для удаления: "))
    except ValueError:
        print("Ошибка: ID должен быть числом.\n")
        return

    task = db.get_task_by_id(task_id)
    if not task:
        print(f"Ошибка: задача с ID {task_id} не найдена.\n")
        return

    confirm = input(f"Удалить задачу '{task.title}'? (y/n): ").strip().lower()
    if confirm in ('y', 'yes', 'да'):
        db.delete_task(task_id)
        print("🗑 Задача удалена.\n")
    else:
        print("Отмена.\n")

def main():
    db = TodoDatabase()
    print("📝 CLI To-Do List")
    print("Данные хранятся в todo.db\n")

    while True:
        print("МЕНЮ:")
        print("1. Показать задачи")
        print("2. Добавить задачу")
        print("3. Переключить статус (выполнено/не выполнено)")
        print("4. Удалить задачу")
        print("0. Выйти")
        choice = input("\nВыберите (0–4): ").strip()

        if choice == "1":
            show_all_tasks(db)
        elif choice == "2":
            add_task_interactive(db)
        elif choice == "3":
            toggle_task_status(db)
        elif choice == "4":
            delete_task_interactive(db)
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Неверный выбор.\n")

if __name__ == "__main__":
    main()