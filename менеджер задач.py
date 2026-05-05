import tkinter as tk
from tkinter import ttk, messagebox
import json
import random
import os
import unittest

# --- Логика работы с задачами ---
class TaskManager:
    def __init__(self, filename='tasks.json'):
        self.filename = filename
        self.tasks = self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_tasks(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=4)

    def add_task(self, title, description, priority):
        if not title or not priority:
            raise ValueError("Заголовок и приоритет обязательны")
        task = {
            "id": random.randint(1000, 9999),
            "title": title,
            "description": description,
            "priority": priority,
            "status": "В работе"
        }
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.save_tasks()

    def filter_tasks(self, status=None, priority=None):
        filtered = self.tasks
        if status:
            filtered = [t for t in filtered if t['status'] == status]
        if priority:
            filtered = [t for t in filtered if t['priority'] == priority]
        return filtered

# --- Графический интерфейс ---
class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")
        self.tm = TaskManager()

        # Виджеты
        self.create_widgets()
        self.update_list()

    def create_widgets(self):
        # Фрейм для ввода
        frame_input = ttk.Frame(self.root, padding="10")
        frame_input.grid(row=0, column=0, sticky="ew")

        ttk.Label(frame_input, text="Заголовок:").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = ttk.Entry(frame_input)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_input, text="Описание:").grid(row=1, column=0, padx=5, pady=5)
        self.desc_entry = ttk.Entry(frame_input)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_input, text="Приоритет:").grid(row=2, column=0, padx=5, pady=5)
        self.priority_var = tk.StringVar(value="Средний")
        priorities = ["Низкий", "Средний", "Высокий"]
        self.priority_menu = ttk.OptionMenu(frame_input, self.priority_var, *priorities)
        self.priority_menu.grid(row=2, column=1, padx=5, pady=5)

        self.add_btn = ttk.Button(frame_input, text="Добавить задачу", command=self.add_task)
        self.add_btn.grid(row=3, columnspan=2, pady=10)

        # Фрейм для фильтров и списка
        frame_list = ttk.Frame(self.root)
        frame_list.grid(row=1, column=0, sticky="nsew")

        # Фильтры
        filter_frame = ttk.Frame(frame_list)
        filter_frame.pack(fill="x", padx=10, pady=5)

        self.filter_status_var = tk.StringVar(value="Все")
        status_options = ["Все", "В работе", "Выполнено"]
        self.filter_status_menu = ttk.OptionMenu(filter_frame, self.filter_status_var, *status_options)
        
        self.filter_priority_var = tk.StringVar(value="Все")
        priority_options = ["Все", "Низкий", "Средний", "Высокий"]
        
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.update_list)
        
        self.filter_status_menu.pack(side="left", padx=5)
        self.filter_priority_menu = ttk.OptionMenu(filter_frame, self.filter_priority_var, *priority_options)
        self.filter_priority_menu.pack(side="left", padx=5)
        
        self.filter_btn.pack(side="left", padx=5)

        # Список задач
        columns = ("ID", "Заголовок", "Описание", "Приоритет", "Статус")
        
        self.tree = ttk.Treeview(frame_list, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=0, width=120 if col=="ID" else 200)
            
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Кнопка удаления
        del_frame = ttk.Frame(frame_list)
        del_frame.pack(fill="x", padx=10, pady=5)
        
        self.delete_btn = ttk.Button(del_frame, text="Удалить выбранную задачу", command=self.delete_selected_task)
        
    def add_task(self):
        try:
            title = self.title_entry.get().strip()
            desc = self.desc_entry.get().strip()
            priority = self.priority_var.get()
            
            if not title or not priority:
                raise ValueError("Заголовок и приоритет обязательны")
                
            self.tm.add_task(title, desc, priority)
            
            # Очистка полей после добавления
            self.title_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            
            messagebox.showinfo("Успех", "Задача добавлена!")
            self.update_list()
            
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))

    def update_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        status = None if self.filter_status_var.get() == "Все" else self.filter_status_var.get()
        priority = None if self.filter_priority_var.get() == "Все" else self.filter_priority_var.get()
            
        tasks = self.tm.filter_tasks(status, priority)
        
        for task in tasks:
            values = (
                task['id'],
                task['title'],
                task['description'],
                task['priority'],
                task['status']
            )
            self.tree.insert("", tk.END, values=values)
    
    def delete_selected_task(self):
        selected_item = self.tree.selection()
        
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления.")
            return
            
        task_id = int(self.tree.item(selected_item)['values'][0])
        
        confirm = messagebox.askyesno("Подтверждение", f"Удалить задачу с ID {task_id}?")
        
        if confirm:
            self.tm.delete_task(task_id)
            messagebox.showinfo("Успех", "Задача удалена.")
            self.update_list()

# --- Тестирование ---
class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.tm = TaskManager('test_tasks.json')
        
    def tearDown(self):
         # Удаляем тестовый файл после тестов
         if os.path.exists('test_tasks.json'):
             os.remove('test_tasks.json')
    
    def test_add_task(self):
         # Проверка добавления задачи
         initial_count = len(self.tm.tasks)
         self.tm.add_task("Тест", "Описание", "Высокий")
         self.assertEqual(len(self.tm.tasks), initial_count + 1)
    
    def test_validation_error(self):
         # Проверка валидации (должна быть ошибка при пустом заголовке)
         with self.assertRaises(ValueError):
             self.tm.add_task("", "Описание", "Низкий")
    
    def test_filter_by_priority(self):
         # Проверка фильтрации по приоритету
         self.tm.add_task("Задача 1", "", "Высокий")
         self.tm.add_task("Задача 2", "", "Низкий")
         
         high_tasks = self.tm.filter_tasks(priority="Высокий")
         low_tasks = self.tm.filter_tasks(priority="Низкий")
         
         self.assertEqual(len(high_tasks), 1)
         self.assertEqual(len(low_tasks), 1)
    
    def test_delete_task(self):
         # Проверка удаления задачи
         initial_count = len(self.tm.tasks)
         
         if initial_count == 0:
             # Если задач нет - создаем одну для теста удаления
             test_task_id = random.randint(1000, 9999)
             test_task = {
                 "id": test_task_id,
                 "title": "Тестовая задача",
                 "description": "",
                 "priority": "Средний",
                 "status": "В работе"
             }
             self.tm.tasks.append(test_task)
             self.tm.save_tasks()
             
             initial_count += 1

         # Удаляем последнюю задачу (по ID из списка)
         last_task_id = self.tm.tasks[-1]['id']
         self.tm.delete_task(last_task_id)
         
         # Проверяем количество задач после удаления
         new_count = len(TaskManager('test_tasks.json').tasks) # Загружаем заново для чистоты теста
         
         # Должно быть на одну задачу меньше (или 0 если была одна)
         expected_count = max(0, initial_count - 1) 
         
         self.assertEqual(new_count, expected_count)


# --- Запуск приложения ---
if __name__ == "__main__":
    # Если запущен с параметром -m unittest (для тестов), не запускать GUI
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
         unittest.main(argv=['first-arg-is-ignored'])
    else:
         root = tk.Tk()
         app = TaskApp(root)
         
         # Настройка растягивания интерфейса при изменении размера окна
         root.grid_rowconfigure(1, weight=1)
         root.grid_columnconfigure(0, weight=1)
         
         root.mainloop()