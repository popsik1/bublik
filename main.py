import json
import os
from tkinter import *
from tkinter import ttk, messagebox

# Получаем путь к папке, где находится программа
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(CURRENT_DIR, "books.json")

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("900x500")
        self.root.resizable(True, True)

        # Данные о книгах
        self.books = []
        self.load_data()

        # Создание интерфейса
        self.create_input_frame()
        self.create_filter_frame()
        self.create_tree_frame()

        # Обновить таблицу
        self.refresh_tree()

    def create_input_frame(self):
        """Фрейм для ввода новой книги"""
        input_frame = LabelFrame(self.root, text="Добавить новую книгу", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Название книги
        Label(input_frame, text="Название книги:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)

        # Автор
        Label(input_frame, text="Автор:").grid(row=0, column=2, sticky="w", pady=2)
        self.author_entry = Entry(input_frame, width=25)
        self.author_entry.grid(row=0, column=3, padx=5, pady=2)

        # Жанр
        Label(input_frame, text="Жанр:").grid(row=1, column=0, sticky="w", pady=2)
        self.genre_entry = Entry(input_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=2)

        # Количество страниц
        Label(input_frame, text="Кол-во страниц:").grid(row=1, column=2, sticky="w", pady=2)
        self.pages_entry = Entry(input_frame, width=25)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=2)

        # Кнопка добавления
        self.add_btn = Button(input_frame, text="Добавить книгу", command=self.add_book, bg="lightgreen")
        self.add_btn.grid(row=2, column=0, columnspan=4, pady=10)

    def create_filter_frame(self):
        """Фрейм для фильтрации"""
        filter_frame = LabelFrame(self.root, text="Фильтрация", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0, sticky="w")
        self.filter_genre_entry = Entry(filter_frame, width=20)
        self.filter_genre_entry.grid(row=0, column=1, padx=5)
        
        # Фильтр по страницам (> N)
        Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.filter_pages_entry = Entry(filter_frame, width=10)
        self.filter_pages_entry.grid(row=0, column=3, padx=5)
        
        # Кнопки фильтрации и сброса
        self.filter_btn = Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=4, padx=5)
        
        self.reset_btn = Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_btn.grid(row=0, column=5, padx=5)

    def create_tree_frame(self):
        """Таблица для отображения книг"""
        tree_frame = Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Скроллбар
        scrollbar = Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Название", "Автор", "Жанр", "Страницы"), 
                                 show="headings", yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)

        # Определение колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Автор", text="Автор")
        self.tree.heading("Жанр", text="Жанр")
        self.tree.heading("Страницы", text="Страницы")

        self.tree.column("ID", width=40)
        self.tree.column("Название", width=200)
        self.tree.column("Автор", width=150)
        self.tree.column("Жанр", width=120)
        self.tree.column("Страницы", width=80)

        self.tree.pack(fill="both", expand=True)

        # Кнопка удаления
        self.delete_btn = Button(self.root, text="Удалить выбранную книгу", command=self.delete_book, bg="salmon")
        self.delete_btn.pack(pady=5)

    def add_book(self):
        """Добавление книги с проверкой ввода"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        # Проверка на пустые поля
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка, что страницы — число
        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        # Создание ID
        new_id = max([book["id"] for book in self.books], default=0) + 1

        # Добавление книги
        new_book = {
            "id": new_id,
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(new_book)
        self.save_data()
        self.refresh_tree()

        # Очистка полей
        self.title_entry.delete(0, END)
        self.author_entry.delete(0, END)
        self.genre_entry.delete(0, END)
        self.pages_entry.delete(0, END)

        messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")

    def apply_filter(self):
        """Применение фильтров"""
        genre_filter = self.filter_genre_entry.get().strip().lower()
        pages_filter_str = self.filter_pages_entry.get().strip()

        filtered_books = self.books.copy()

        # Фильтр по жанру
        if genre_filter:
            filtered_books = [book for book in filtered_books if genre_filter in book["genre"].lower()]

        # Фильтр по количеству страниц (> N)
        if pages_filter_str:
            try:
                pages_min = int(pages_filter_str)
                filtered_books = [book for book in filtered_books if book["pages"] > pages_min]
            except ValueError:
                messagebox.showerror("Ошибка", "Фильтр страниц должен быть числом!")
                return

        self.display_books(filtered_books)

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_genre_entry.delete(0, END)
        self.filter_pages_entry.delete(0, END)
        self.refresh_tree()

    def refresh_tree(self):
        """Показать все книги"""
        self.display_books(self.books)

    def display_books(self, books):
        """Отобразить книги в таблице"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in books:
            self.tree.insert("", END, values=(book["id"], book["title"], book["author"], 
                                              book["genre"], book["pages"]))

    def delete_book(self):
        """Удалить выбранную книгу"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return

        # Получаем ID книги
        item = self.tree.item(selected[0])
        book_id = item["values"][0]

        # Удаляем из списка
        self.books = [book for book in self.books if book["id"] != book_id]
        self.save_data()
        self.refresh_tree()
        messagebox.showinfo("Успех", "Книга удалена!")

    def save_data(self):
        """Сохранить данные в JSON"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            print(f"Данные сохранены в: {DATA_FILE}")  # Отладка
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}\nПуть: {DATA_FILE}")

    def load_data(self):
        """Загрузить данные из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
                print(f"Данные загружены из: {DATA_FILE}")  # Отладка
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Ошибка загрузки: {e}")
                self.books = []
        else:
            print(f"Файл {DATA_FILE} не найден, создаём новый список")
            self.books = []
            # Создаём пустой JSON файл
            self.save_data()

if __name__ == "__main__":
    root = Tk()
    app = BookTracker(root)
    root.mainloop()