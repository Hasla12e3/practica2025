import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import psycopg2

# Параметры подключения к базе данных PostgreSQL
DB_SETTINGS = {
    "host": "localhost",
    "database": "Техникум",  # Используйте вашу базу данных
    "user": "postgres",
    "password": "1234"
}

# Функция для подключения к базе данных
def get_connection():
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        return conn
    except Exception as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных:\n{e}")
        return None

# Функция для отображения данных из таблицы в Treeview
def show_table_data(tree, query):
    conn = get_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]  # Заголовки колонок

        # Очищаем Treeview перед заполнением новыми данными
        tree.delete(*tree.get_children())

        # Устанавливаем колонки в Treeview
        tree["columns"] = columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        # Заполняем Treeview данными
        for row in rows:
            tree.insert("", "end", values=row)

        cursor.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")
        if conn:
            conn.close()

# Функция для создания вкладки с таблицей
def create_tab(notebook, table_name, query):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=table_name)

    # Создаем Treeview для отображения данных
    tree = ttk.Treeview(frame, show="headings", height=15)
    tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Загружаем данные в Treeview
    show_table_data(tree, query)

    # Кнопки для управления данными
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill=tk.X, padx=10, pady=5)

    if table_name == "Группы":
        add_button = ttk.Button(button_frame, text="Добавить", command=lambda: add("группы", ["Группа", "Количество человек"], tree))
        delete_button = ttk.Button(button_frame, text="Удалить", command=lambda: delete("группы", "Группа", tree))
        edit_button = ttk.Button(button_frame, text="Редактировать", command=lambda: edit("группы", ["Группа", "Количество человек"], "Группа", tree))
    elif table_name == "Дисциплины":
        add_button = ttk.Button(button_frame, text="Добавить", command=lambda: add("дисциплины", ["Дисциплина", "Группа", "Количество пар"], tree))
        delete_button = ttk.Button(button_frame, text="Удалить", command=lambda: delete("дисциплины", "Дисциплина", tree))
        edit_button = ttk.Button(button_frame, text="Редактировать", command=lambda: edit("дисциплины", ["Дисциплина", "Группа", "Количество пар"], "Дисциплина", tree))
    elif table_name == "Кабинеты":
        add_button = ttk.Button(button_frame, text="Добавить", command=lambda: add("кабинеты", ["Номер кабинета", "Описание кабинета", "Количество мест", "Примечания"], tree))
        delete_button = ttk.Button(button_frame, text="Удалить", command=lambda: delete("кабинеты", "Номер кабинета", tree))
        edit_button = ttk.Button(button_frame, text="Редактировать", command=lambda: edit("кабинеты", ["Номер кабинета", "Описание кабинета", "Количество мест", "Примечания"], "Номер кабинета", tree))
    elif table_name == "Преподаватели":
        add_button = ttk.Button(button_frame, text="Добавить", command=lambda: add("преподаватели", ["ФИО преподавателя"], tree))
        delete_button = ttk.Button(button_frame, text="Удалить", command=lambda: delete("преподаватели", "ФИО преподавателя", tree))
        edit_button = ttk.Button(button_frame, text="Редактировать", command=lambda: edit("преподаватели", ["ФИО преподавателя"], "ФИО преподавателя", tree))

    add_button.pack(side=tk.LEFT, padx=5)
    delete_button.pack(side=tk.LEFT, padx=5)
    edit_button.pack(side=tk.LEFT, padx=5)

# Функция для добавления записи в таблицу
def add(table_name, columns, tree):
    def save_record():
        conn = get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            values = [entry.get() for entry in entries]
            quoted_columns = [f'"{col}"' for col in columns]
            query = f"INSERT INTO \"{table_name}\" ({', '.join(quoted_columns)}) VALUES ({', '.join(['%s'] * len(values))})"
            cursor.execute(query, values)
            conn.commit()
            messagebox.showinfo("Успех", "Запись успешно добавлена")
            add_window.destroy()
            show_table_data(tree, f"SELECT * FROM \"{table_name}\"")
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить запись:\n{e}")
            if conn:
                conn.close()

    add_window = tk.Toplevel()
    add_window.title(f"Добавить запись в {table_name}")

    entries = []
    for i, col in enumerate(columns):
        tk.Label(add_window, text=col).grid(row=i, column=0, padx=10, pady=5)
        entry = tk.Entry(add_window)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries.append(entry)

    tk.Button(add_window, text="Добавить", command=save_record).grid(row=len(columns), column=0, columnspan=2, pady=10)

# Функция для удаления записи из таблицы
def delete(table_name, id_column, tree):
    def delete_record():
        conn = get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            query = f"DELETE FROM \"{table_name}\" WHERE \"{id_column}\" = %s"
            cursor.execute(query, (entry_id.get(),))
            conn.commit()
            messagebox.showinfo("Успех", "Запись успешно удалена")
            delete_window.destroy()
            show_table_data(tree, f"SELECT * FROM \"{table_name}\"")
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить запись:\n{e}")
            if conn:
                conn.close()

    delete_window = tk.Toplevel()
    delete_window.title(f"Удалить запись из {table_name}")

    tk.Label(delete_window, text=f"Введите {id_column}:").grid(row=0, column=0, padx=10, pady=5)
    entry_id = tk.Entry(delete_window)
    entry_id.grid(row=0, column=1, padx=10, pady=5)

    tk.Button(delete_window, text="Удалить", command=delete_record).grid(row=1, column=0, columnspan=2, pady=10)

# Функция для редактирования записи в таблице
def edit(table_name, columns, id_column, tree):
    def save_changes():
        conn = get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            values = [entry.get() for entry in entries]
            set_clause = ', '.join([f"\"{col}\" = %s" for col in columns])
            query = f"UPDATE \"{table_name}\" SET {set_clause} WHERE \"{id_column}\" = %s"
            cursor.execute(query, values + [entry_id.get()])
            conn.commit()
            messagebox.showinfo("Успех", "Запись успешно обновлена")
            edit_window.destroy()
            show_table_data(tree, f"SELECT * FROM \"{table_name}\"")
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить запись:\n{e}")
            if conn:
                conn.close()

    edit_window = tk.Toplevel()
    edit_window.title(f"Редактировать запись в {table_name}")

    tk.Label(edit_window, text=f"Введите {id_column}:").grid(row=0, column=0, padx=10, pady=5)
    entry_id = tk.Entry(edit_window)
    entry_id.grid(row=0, column=1, padx=10, pady=5)

    entries = []
    for i, col in enumerate(columns):
        tk.Label(edit_window, text=col).grid(row=i+1, column=0, padx=10, pady=5)
        entry = tk.Entry(edit_window)
        entry.grid(row=i+1, column=1, padx=10, pady=5)
        entries.append(entry)

    tk.Button(edit_window, text="Сохранить", command=save_changes).grid(row=len(columns)+1, column=0, columnspan=2, pady=10)

# Главное окно с вкладками
def create_main_window():
    root = tk.Tk()
    root.title("Техникум")
    root.geometry("800x800")

    # Загружаем изображение (логотип учебного заведения)
    logo_path = r"C:\Users\dsawr\Desktop\Practica\hiik_sibguti.png"  # Путь к изображению
    try:
        logo_image = Image.open(logo_path)
        logo_image = logo_image.resize((400, 250))  # Изменение размера изображения
        logo_photo = ImageTk.PhotoImage(logo_image)

        # Создаем метку для отображения логотипа
        logo_label = tk.Label(root, image=logo_photo)
        logo_label.image = logo_photo  # Сохраняем ссылку на изображение
        logo_label.pack(pady=20)  # Отображаем логотип с отступом сверху
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")

    # Создаем Notebook для вкладок
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Вкладка "Группы"
    create_tab(notebook, "Группы", """
    SELECT g."Группа", g."Количество человек"
    FROM "группы" g;
    """)

    # Вкладка "Дисциплины"
    create_tab(notebook, "Дисциплины", """
    SELECT d."Дисциплина", g."Группа", d."Количество пар"
    FROM "дисциплины" d
    JOIN "группы" g ON d."Группа" = g."Группа";
    """)

    # Вкладка "Кабинеты"
    create_tab(notebook, "Кабинеты", """
    SELECT r."Номер кабинета", r."Описание кабинета", r."Количество мест", r."Примечания"
    FROM "кабинеты" r;
    """)

    # Вкладка "Преподаватели"
    create_tab(notebook, "Преподаватели", """
    SELECT t."ФИО преподавателя"
    FROM "преподаватели" t;
    """)

    root.mainloop()

# Запуск программы
if __name__ == "__main__":
    create_main_window()  # Открываем главное окно