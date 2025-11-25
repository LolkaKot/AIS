import flet as ft
import sqlite3
import datetime
from datetime import date
import os
import json
import webbrowser
import shutil
from pathlib import Path

class HelpSystem:
    def __init__(self):
        self.help_url = "https://lolkakot.github.io/help_system/"
        
    def open_help(self, page: ft.Page):
        """Открытие справочной системы"""
        try:
            webbrowser.open(self.help_url)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Справка открыта в браузере")
            )
            page.snack_bar.open = True
            page.update()
            
        except Exception as e:
            print(f"Ошибка при открытии справки: {e}")
            self.show_help_error(page, f"Ошибка открытия справки: {str(e)}")
    
    def show_help_error(self, page: ft.Page, message: str):
        """Показать ошибку открытия справки"""
        error_dialog = ft.AlertDialog(
            title=ft.Text("Ошибка справки"),
            content=ft.Column([
                ft.Text(message),
                ft.Divider(),
                ft.Text("Попробуйте открыть ссылку вручную:"),
                ft.Text(self.help_url, style=ft.TextStyle(weight=ft.FontWeight.BOLD)),
            ], tight=True),
            actions=[
                ft.TextButton("Открыть вручную", on_click=lambda e: webbrowser.open(self.help_url)),
                ft.TextButton("OK", on_click=lambda e: page.close(error_dialog))
            ]
        )
        page.open(error_dialog)

class ComputerStoreDB:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    full_name TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category_id INTEGER,
                    manufacturer TEXT,
                    price REAL NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    min_quantity INTEGER DEFAULT 0,
                    description TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS income_invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    supplier_id INTEGER,
                    invoice_date DATE NOT NULL,
                    total_amount REAL DEFAULT 0,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS income_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (invoice_id) REFERENCES income_invoices (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS outcome_invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    customer_name TEXT,
                    invoice_date DATE NOT NULL,
                    total_amount REAL DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS outcome_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (invoice_id) REFERENCES outcome_invoices (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, password, role, full_name)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin', 'admin', 'Администратор'))
            
            categories = ['Компьютеры', 'Ноутбуки', 'Комплектующие', 'Периферия', 'Программное обеспечение']
            for category in categories:
                cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
            
            conn.commit()
            print("База данных успешно инициализирована")
            
        except Exception as e:
            print(f"Ошибка инициализации базы данных: {e}")
        finally:
            conn.close()

class ComputerStoreApp:
    def __init__(self):
        self.db = ComputerStoreDB()
        self.current_user = None
        self.help_system = HelpSystem()
        self.is_logged_in = False
        
    def main(self, page: ft.Page):
        self.page = page
        self.page.title = "АИС Компьютерный салон"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.fonts = {
            "Roboto": "Roboto"
        }
        
        self.main_content = ft.Column(expand=True, scroll=ft.ScrollMode.ADAPTIVE)
        
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME,
                    selected_icon=ft.Icons.HOME,
                    label="Главная"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE,
                    selected_icon=ft.Icons.PEOPLE,
                    label="Поставщики"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.INVENTORY_2,
                    selected_icon=ft.Icons.INVENTORY_2,
                    label="Товары"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.INPUT,
                    selected_icon=ft.Icons.INPUT,
                    label="Приход"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.OUTPUT,
                    selected_icon=ft.Icons.OUTPUT,
                    label="Расход"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ANALYTICS,
                    selected_icon=ft.Icons.ANALYTICS,
                    label="Отчеты"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.BACKUP,
                    selected_icon=ft.Icons.BACKUP,
                    label="Резервная копия"
                ),
            ],
            on_change=self.navigate
        )
        
        self.app_bar = ft.AppBar(
            title=ft.Text("АИС Компьютерный салон"),
            center_title=False,
            bgcolor=ft.Colors.BLACK,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.HELP_OUTLINE,
                    tooltip="Справка",
                    on_click=lambda _: self.show_help()
                ),
                ft.IconButton(ft.Icons.ACCOUNT_CIRCLE, on_click=self.show_user_info),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(text="О программе", on_click=self.show_about),
                        ft.PopupMenuItem(text="Справка", on_click=lambda _: self.show_help()),
                        ft.PopupMenuItem(),
                        ft.PopupMenuItem(text="Выход", on_click=self.logout),
                    ]
                )
            ]
        )
        
        content = ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                ft.Container(
                    content=self.main_content,
                    expand=True,
                    padding=20
                ),
            ],
            expand=True,
        )
        
        self.page.add(self.app_bar, content)
        self.show_login_page()
    
    def show_snack_bar(self, message):
        """Показать уведомление"""
        snack_bar = ft.SnackBar(content=ft.Text(message), action="OK")
        self.page.snack_bar = snack_bar
        snack_bar.open = True
        self.page.update()
    
    def show_help(self):
        """Показать справку"""
        self.help_system.open_help(self.page)
    
    def show_login_page(self):
        """Показать страницу входа"""
        self.is_logged_in = False
        self.main_content.controls.clear()
        
        self.login_field = ft.TextField(label="Логин", prefix_icon=ft.Icons.PERSON)
        self.password_field = ft.TextField(label="Пароль", password=True, prefix_icon=ft.Icons.LOCK)
        
        login_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Вход в систему", size=24, weight=ft.FontWeight.BOLD),
                    self.login_field,
                    self.password_field,
                    ft.ElevatedButton(
                        "Войти",
                        on_click=self.login,
                        style=ft.ButtonStyle(
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_700
                        )
                    )
                ], width=300, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                margin=20
            ),
            width=400
        )
        
        self.main_content.controls.append(
            ft.Container(
                content=login_card,
                alignment=ft.alignment.center,
                expand=True
            )
        )
        self.page.update()
    
    def login(self, e):
        """Обработка входа в систему"""
        username = self.login_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.show_snack_bar("Введите логин и пароль")
            return
        
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                self.current_user = {
                    "id": user[0],
                    "username": user[1],
                    "role": user[3],
                    "full_name": user[4]
                }
                self.is_logged_in = True
                self.show_main_page()
                self.show_snack_bar(f"Добро пожаловать, {user[4]}!")
            else:
                self.show_snack_bar("Неверный логин или пароль")
        except Exception as e:
            self.show_snack_bar(f"Ошибка базы данных: {e}")
    
    def logout(self, e):
        """Выход из системы"""
        self.current_user = None
        self.is_logged_in = False
        self.show_login_page()
        self.show_snack_bar("Вы вышли из системы")
    
    def navigate(self, e):
        """Навигация по разделам с проверкой авторизации"""
        if not self.is_logged_in:
            self.show_snack_bar("Для доступа к этому разделу необходимо авторизоваться")
            self.nav_rail.selected_index = None
            self.page.update()
            return
            
        index = e.control.selected_index
        self.main_content.controls.clear()
        
        if index == 0:
            self.show_main_page()
        elif index == 1:
            self.show_suppliers()
        elif index == 2:
            self.show_products()
        elif index == 3:
            self.show_income()
        elif index == 4:
            self.show_outcome()
        elif index == 5:
            self.show_reports()
        elif index == 6:
            self.show_backup()
        
        self.page.update()
    
    def show_main_page(self):
        """Показать главную страницу"""
        self.main_content.controls.clear()
        
        stats = self.get_stats()
        
        stats_row = ft.ResponsiveRow([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INVENTORY_2, size=40, color=ft.Colors.BLUE_400),
                    ft.Text("Всего товаров", size=16),
                    ft.Text(str(stats['total_products']), size=24, weight=ft.FontWeight.BOLD)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                margin=5,
                bgcolor=ft.Colors.BLACK,
                border_radius=10,
                col=3
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING, size=40, color=ft.Colors.ORANGE_400),
                    ft.Text("Товары с низким запасом", size=16),
                    ft.Text(str(stats['low_stock']), size=24, weight=ft.FontWeight.BOLD)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                margin=5,
                bgcolor=ft.Colors.BLACK,
                border_radius=10,
                col=3
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INPUT, size=40, color=ft.Colors.GREEN_400),
                    ft.Text("Приход за месяц", size=16),
                    ft.Text(str(stats['month_income']), size=24, weight=ft.FontWeight.BOLD)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                margin=5,
                bgcolor=ft.Colors.BLACK,
                border_radius=10,
                col=3
            ),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.OUTPUT, size=40, color=ft.Colors.RED_400),
                    ft.Text("Расход за месяц", size=16),
                    ft.Text(str(stats['month_outcome']), size=24, weight=ft.FontWeight.BOLD)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                margin=5,
                bgcolor=ft.Colors.BLACK,
                border_radius=10,
                col=3
            ),
        ])
        
        self.main_content.controls.extend([
            ft.Text("Главная панель", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            stats_row,
            ft.Container(
                content=ft.Text("Быстрые действия", size=20, weight=ft.FontWeight.BOLD),
                margin=ft.margin.only(top=20)
            ),
            ft.ResponsiveRow([
                ft.ElevatedButton(
                    "Добавить товар",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: self.show_products(),
                    col=4,
                    style=ft.ButtonStyle(padding=20)
                ),
                ft.ElevatedButton(
                    "Создать приход",
                    icon=ft.Icons.INPUT,
                    on_click=lambda _: self.show_income(),
                    col=4,
                    style=ft.ButtonStyle(padding=20)
                ),
                ft.ElevatedButton(
                    "Создать расход",
                    icon=ft.Icons.OUTPUT,
                    on_click=lambda _: self.show_outcome(),
                    col=4,
                    style=ft.ButtonStyle(padding=20)
                ),
            ])
        ])
        self.page.update()

    def get_stats(self):
        """Получить статистику для главной страницы"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM products")
            total_products = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= min_quantity AND min_quantity > 0")
            low_stock = cursor.fetchone()[0]
            
            month_start = date.today().replace(day=1)
            cursor.execute("SELECT COUNT(*) FROM income_invoices WHERE invoice_date >= ?", (month_start.isoformat(),))
            month_income = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM outcome_invoices WHERE invoice_date >= ?", (month_start.isoformat(),))
            month_outcome = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_products': total_products,
                'low_stock': low_stock,
                'month_income': month_income,
                'month_outcome': month_outcome
            }
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {
                'total_products': 0,
                'low_stock': 0,
                'month_income': 0,
                'month_outcome': 0
            }

    def show_suppliers(self):
        """Показать раздел поставщиков"""
        self.main_content.controls.clear()
        self.main_content.controls.append(ft.Text("Управление поставщиков", size=28, weight=ft.FontWeight.BOLD))
        self.main_content.controls.append(ft.Divider())
        
        add_button = ft.ElevatedButton("Добавить поставщика", icon=ft.Icons.ADD, on_click=self.add_supplier)
        self.main_content.controls.append(add_button)
        
        try:
            suppliers = self.get_suppliers()
            if suppliers:
                data_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Название")),
                        ft.DataColumn(ft.Text("Контактное лицо")),
                        ft.DataColumn(ft.Text("Телефон")),
                        ft.DataColumn(ft.Text("Действия")),
                    ],
                    rows=[]
                )
                
                for supplier in suppliers:
                    data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(supplier[0]))),
                                ft.DataCell(ft.Text(supplier[1])),
                                ft.DataCell(ft.Text(supplier[2] or "")),
                                ft.DataCell(ft.Text(supplier[3] or "")),
                                ft.DataCell(ft.Row([
                                    ft.IconButton(ft.Icons.EDIT, on_click=lambda e, sid=supplier[0]: self.edit_supplier(sid)),
                                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, sid=supplier[0]: self.delete_supplier(sid)),
                                ])),
                            ]
                        )
                    )
                
                self.main_content.controls.append(ft.Container(
                    content=data_table,
                    margin=ft.margin.only(top=20)
                ))
            else:
                self.main_content.controls.append(ft.Text("Нет поставщиков", style=ft.TextStyle(italic=True)))
        except Exception as e:
            self.main_content.controls.append(ft.Text(f"Ошибка загрузки поставщиков: {e}", color=ft.Colors.RED))
        
        self.page.update()
    
    def get_suppliers(self):
        """Получить список поставщиков"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers ORDER BY name")
            suppliers = cursor.fetchall()
            conn.close()
            return suppliers
        except Exception as e:
            print(f"Ошибка получения поставщиков: {e}")
            return []
    
    def add_supplier(self, e):
        """Добавить поставщика"""
        def save_supplier(e):
            name = name_field.value
            contact = contact_field.value
            phone = phone_field.value
            email = email_field.value
            address = address_field.value
            
            if not name:
                self.show_snack_bar("Введите название поставщика")
                return
            
            try:
                conn = sqlite3.connect('computer_store.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO suppliers (name, contact_person, phone, email, address)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, contact, phone, email, address))
                conn.commit()
                conn.close()
                
                self.page.close(dialog)
                self.show_suppliers()
                self.show_snack_bar("Поставщик добавлен")
            except Exception as ex:
                self.show_snack_bar(f"Ошибка добавления поставщика: {ex}")
        
        name_field = ft.TextField(label="Название*", width=400)
        contact_field = ft.TextField(label="Контактное лицо", width=400)
        phone_field = ft.TextField(label="Телефон", width=400)
        email_field = ft.TextField(label="Email", width=400)
        address_field = ft.TextField(label="Адрес", multiline=True, width=400)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить поставщика"),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    contact_field,
                    phone_field,
                    email_field,
                    address_field,
                ], scroll=ft.ScrollMode.ADAPTIVE),
                width=400,
                height=400
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Сохранить", on_click=save_supplier),
            ]
        )
        self.page.open(dialog)
    
    def edit_supplier(self, supplier_id):
        """Редактировать поставщика"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
            supplier = cursor.fetchone()
            conn.close()
            
            if not supplier:
                self.show_snack_bar("Поставщик не найден")
                return
            
            def save_edit(e):
                name = name_field.value
                contact = contact_field.value
                phone = phone_field.value
                email = email_field.value
                address = address_field.value
                
                if not name:
                    self.show_snack_bar("Введите название поставщика")
                    return
                
                try:
                    conn = sqlite3.connect('computer_store.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE suppliers 
                        SET name=?, contact_person=?, phone=?, email=?, address=?
                        WHERE id=?
                    ''', (name, contact, phone, email, address, supplier_id))
                    conn.commit()
                    conn.close()
                    
                    self.page.close(dialog)
                    self.show_suppliers()
                    self.show_snack_bar("Поставщик обновлен")
                except Exception as ex:
                    self.show_snack_bar(f"Ошибка обновления поставщика: {ex}")
            
            name_field = ft.TextField(label="Название*", width=400, value=supplier[1])
            contact_field = ft.TextField(label="Контактное лицо", width=400, value=supplier[2] or "")
            phone_field = ft.TextField(label="Телефон", width=400, value=supplier[3] or "")
            email_field = ft.TextField(label="Email", width=400, value=supplier[4] or "")
            address_field = ft.TextField(label="Адрес", multiline=True, width=400, value=supplier[5] or "")
            
            dialog = ft.AlertDialog(
                title=ft.Text("Редактировать поставщика"),
                content=ft.Container(
                    content=ft.Column([
                        name_field,
                        contact_field,
                        phone_field,
                        email_field,
                        address_field,
                    ], scroll=ft.ScrollMode.ADAPTIVE),
                    width=400,
                    height=400
                ),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                    ft.TextButton("Сохранить", on_click=save_edit),
                ]
            )
            self.page.open(dialog)
        except Exception as e:
            self.show_snack_bar(f"Ошибка редактирования поставщика: {e}")
    
    def delete_supplier(self, supplier_id):
        """Удалить поставщика"""
        def confirm_delete(e):
            try:
                conn = sqlite3.connect('computer_store.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
                conn.commit()
                conn.close()
                
                self.page.close(dialog)
                self.show_suppliers()
                self.show_snack_bar("Поставщик удален")
            except Exception as ex:
                self.show_snack_bar(f"Ошибка удаления поставщика: {ex}")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Подтверждение удаления"),
            content=ft.Text("Вы уверены, что хотите удалить этого поставщика?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Удалить", on_click=confirm_delete),
            ]
        )
        self.page.open(dialog)
    
    def show_products(self):
        """Показать раздел товаров"""
        self.main_content.controls.clear()
        self.main_content.controls.append(ft.Text("Управление товарами", size=28, weight=ft.FontWeight.BOLD))
        self.main_content.controls.append(ft.Divider())
        
        add_button = ft.ElevatedButton("Добавить товар", icon=ft.Icons.ADD, on_click=self.add_product)
        self.main_content.controls.append(add_button)
        
        try:
            products = self.get_products()
            if products:
                data_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("ID")),
                        ft.DataColumn(ft.Text("Название")),
                        ft.DataColumn(ft.Text("Категория")),
                        ft.DataColumn(ft.Text("Производитель")),
                        ft.DataColumn(ft.Text("Цена")),
                        ft.DataColumn(ft.Text("Остаток")),
                        ft.DataColumn(ft.Text("Действия")),
                    ],
                    rows=[]
                )
                
                categories = self.get_categories_dict()
                
                for product in products:
                    category_name = categories.get(product[2], "Не указана")
                    data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(product[0]))),
                                ft.DataCell(ft.Text(product[1])),
                                ft.DataCell(ft.Text(category_name)),
                                ft.DataCell(ft.Text(product[3] or "")),
                                ft.DataCell(ft.Text(f"{product[4]:.2f} руб.")),
                                ft.DataCell(ft.Text(str(product[5]))),
                                ft.DataCell(ft.Row([
                                    ft.IconButton(ft.Icons.EDIT, on_click=lambda e, pid=product[0]: self.edit_product(pid)),
                                    ft.IconButton(ft.Icons.DELETE, on_click=lambda e, pid=product[0]: self.delete_product(pid)),
                                ])),
                            ]
                        )
                    )
                
                self.main_content.controls.append(ft.Container(
                    content=data_table,
                    margin=ft.margin.only(top=20)
                ))
            else:
                self.main_content.controls.append(ft.Text("Нет товаров", style=ft.TextStyle(italic=True)))
        except Exception as e:
            self.main_content.controls.append(ft.Text(f"Ошибка загрузки товаров: {e}", color=ft.Colors.RED))
        
        self.page.update()
    
    def get_categories_dict(self):
        """Получить словарь категорий - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()
            conn.close()
            return {cat[0]: cat[1] for cat in categories}
        except Exception as e:
            print(f"Ошибка получения категорий: {e}")
            return {}
    
    def get_categories_list(self):
        """Получить список категорий для выпадающего списка - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()
            conn.close()
            
            options = [ft.dropdown.Option(key="", text="Не выбрано")]
            for cat_id, cat_name in categories:
                options.append(ft.dropdown.Option(key=str(cat_id), text=cat_name))
            return options
        except Exception as e:
            print(f"Ошибка получения списка категорий: {e}")
            return [ft.dropdown.Option(key="", text="Не выбрано")]
    
    def get_products(self):
        """Получить список товаров"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products ORDER BY name")
            products = cursor.fetchall()
            conn.close()
            return products
        except Exception as e:
            print(f"Ошибка получения товаров: {e}")
            return []
    
    def add_product(self, e):
        """Добавить товар"""
        def save_product(e):
            name = name_field.value
            category = category_field.value
            manufacturer = manufacturer_field.value
            price = price_field.value
            quantity = quantity_field.value
            min_quantity = min_quantity_field.value
            description = description_field.value
            
            if not name or not price:
                self.show_snack_bar("Заполните обязательные поля")
                return
            
            try:
                price = float(price)
                quantity = int(quantity) if quantity else 0
                min_quantity = int(min_quantity) if min_quantity else 0
            except ValueError:
                self.show_snack_bar("Некорректные числовые значения")
                return
            
            try:
                conn = sqlite3.connect('computer_store.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO products (name, category_id, manufacturer, price, quantity, min_quantity, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, category, manufacturer, price, quantity, min_quantity, description))
                conn.commit()
                conn.close()
                
                self.page.close(dialog)
                self.show_products()
                self.show_snack_bar("Товар добавлен")
            except Exception as ex:
                self.show_snack_bar(f"Ошибка добавления товара: {ex}")
        
        # Используем исправленный метод для получения категорий
        category_options = self.get_categories_list()
        
        name_field = ft.TextField(label="Название*", width=400)
        category_field = ft.Dropdown(label="Категория", width=400, options=category_options)
        manufacturer_field = ft.TextField(label="Производитель", width=400)
        price_field = ft.TextField(label="Цена*", width=400)
        quantity_field = ft.TextField(label="Количество", width=400, value="0")
        min_quantity_field = ft.TextField(label="Мин. количество", width=400, value="0")
        description_field = ft.TextField(label="Описание", multiline=True, width=400)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Добавить товар"),
            content=ft.Container(
                content=ft.Column([
                    name_field,
                    category_field,
                    manufacturer_field,
                    price_field,
                    quantity_field,
                    min_quantity_field,
                    description_field,
                ], scroll=ft.ScrollMode.ADAPTIVE),
                width=400,
                height=500
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Сохранить", on_click=save_product),
            ]
        )
        self.page.open(dialog)
    
    def edit_product(self, product_id):
        """Редактировать товар"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = cursor.fetchone()
            conn.close()
            
            if not product:
                self.show_snack_bar("Товар не найден")
                return
            
            def save_edit(e):
                name = name_field.value
                category = category_field.value
                manufacturer = manufacturer_field.value
                price = price_field.value
                quantity = quantity_field.value
                min_quantity = min_quantity_field.value
                description = description_field.value
                
                if not name or not price:
                    self.show_snack_bar("Заполните обязательные поля")
                    return
                
                try:
                    price = float(price)
                    quantity = int(quantity) if quantity else 0
                    min_quantity = int(min_quantity) if min_quantity else 0
                except ValueError:
                    self.show_snack_bar("Некорректные числовые значения")
                    return
                
                try:
                    conn = sqlite3.connect('computer_store.db')
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE products 
                        SET name=?, category_id=?, manufacturer=?, price=?, quantity=?, min_quantity=?, description=?
                        WHERE id=?
                    ''', (name, category, manufacturer, price, quantity, min_quantity, description, product_id))
                    conn.commit()
                    conn.close()
                    
                    self.page.close(dialog)
                    self.show_products()
                    self.show_snack_bar("Товар обновлен")
                except Exception as ex:
                    self.show_snack_bar(f"Ошибка обновления товара: {ex}")
            
            # Используем исправленный метод для получения категорий
            category_options = self.get_categories_list()
            
            name_field = ft.TextField(label="Название*", width=400, value=product[1])
            category_field = ft.Dropdown(
                label="Категория", 
                width=400, 
                options=category_options,
                value=str(product[2]) if product[2] else ""
            )
            manufacturer_field = ft.TextField(label="Производитель", width=400, value=product[3] or "")
            price_field = ft.TextField(label="Цена*", width=400, value=str(product[4]))
            quantity_field = ft.TextField(label="Количество", width=400, value=str(product[5]))
            min_quantity_field = ft.TextField(label="Мин. количество", width=400, value=str(product[6]))
            description_field = ft.TextField(label="Описание", multiline=True, width=400, value=product[7] or "")
            
            dialog = ft.AlertDialog(
                title=ft.Text("Редактировать товар"),
                content=ft.Container(
                    content=ft.Column([
                        name_field,
                        category_field,
                        manufacturer_field,
                        price_field,
                        quantity_field,
                        min_quantity_field,
                        description_field,
                    ], scroll=ft.ScrollMode.ADAPTIVE),
                    width=400,
                    height=500
                ),
                actions=[
                    ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                    ft.TextButton("Сохранить", on_click=save_edit),
                ]
            )
            self.page.open(dialog)
        except Exception as e:
            self.show_snack_bar(f"Ошибка редактирования товара: {e}")
    
    def delete_product(self, product_id):
        """Удалить товар"""
        def confirm_delete(e):
            try:
                conn = sqlite3.connect('computer_store.db')
                cursor = conn.cursor()
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                conn.close()
                
                self.page.close(dialog)
                self.show_products()
                self.show_snack_bar("Товар удален")
            except Exception as ex:
                self.show_snack_bar(f"Ошибка удаления товара: {ex}")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Подтверждение удаления"),
            content=ft.Text("Вы уверены, что хотите удалить этот товар?"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Удалить", on_click=confirm_delete),
            ]
        )
        self.page.open(dialog)
    
    def show_income(self):
        """Показать раздел прихода с функциональными кнопками"""
        self.main_content.controls.clear()
        self.main_content.controls.append(ft.Text("Учет прихода товаров", size=28, weight=ft.FontWeight.BOLD))
        self.main_content.controls.append(ft.Divider())
        
        self.main_content.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("Функционал учета прихода", size=20),
                    ft.Text("Создание приходных накладных"),
                    ft.Text("Выбор поставщика"),
                    ft.Text("Добавление позиций товаров"),
                    ft.ElevatedButton("Создать приходную накладную", icon=ft.Icons.ADD, on_click=self.create_income_invoice),
                ]),
                padding=20,
                bgcolor=ft.Colors.BLACK,
                border_radius=10
            )
        )
        self.page.update()
    
    def create_income_invoice(self, e):
        """Создать приходную накладную - РАБОЧАЯ ВЕРСИЯ"""
        def save_invoice(e):
            try:
                invoice_number = invoice_number_field.value
                supplier_id = supplier_field.value
                invoice_date = date_field.value
                
                if not invoice_number or not invoice_date:
                    self.show_snack_bar("Заполните обязательные поля")
                    return
                
                conn = sqlite3.connect('computer_store.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO income_invoices (invoice_number, supplier_id, invoice_date, total_amount)
                    VALUES (?, ?, ?, ?)
                ''', (invoice_number, supplier_id, invoice_date, 0))
                conn.commit()
                conn.close()
                
                self.page.close(dialog)
                self.show_income()
                self.show_snack_bar("Приходная накладная создана")
            except Exception as ex:
                self.show_snack_bar(f"Ошибка создания накладной: {ex}")
        
        # Получаем список поставщиков
        suppliers = self.get_suppliers()
        supplier_options = [ft.dropdown.Option(key="", text="Не выбран")]
        for supplier in suppliers:
            supplier_options.append(ft.dropdown.Option(key=str(supplier[0]), text=supplier[1]))
        
        invoice_number_field = ft.TextField(label="Номер накладной*", width=400)
        supplier_field = ft.Dropdown(label="Поставщик", width=400, options=supplier_options)
        date_field = ft.TextField(
            label="Дата накладной*", 
            width=400, 
            value=date.today().isoformat(),
            hint_text="ГГГГ-ММ-ДД"
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Создать приходную накладную"),
            content=ft.Container(
                content=ft.Column([
                    invoice_number_field,
                    supplier_field,
                    date_field,
                ]),
                width=400
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Сохранить", on_click=save_invoice),
            ]
        )
        self.page.open(dialog)
    
    def show_outcome(self):
        """Показать раздел расхода с функциональными кнопками"""
        self.main_content.controls.clear()
        self.main_content.controls.append(ft.Text("Учет расхода товаров", size=28, weight=ft.FontWeight.BOLD))
        self.main_content.controls.append(ft.Divider())
        
        self.main_content.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("Функционал учета расхода", size=20),
                    ft.Text("Создание расходных накладных"),
                    ft.Text("Регистрация продаж"),
                    ft.Text("Управление клиентами"),
                    ft.ElevatedButton("Создать расходную накладную", icon=ft.Icons.ADD, on_click=self.create_outcome_invoice),
                ]),
                padding=20,
                bgcolor=ft.Colors.BLACK,
                border_radius=10
            )
        )
        self.page.update()
    
    def create_outcome_invoice(self, e):
        """Создать расходную накладную - РАБОЧАЯ ВЕРСИЯ"""
        def save_invoice(e):
            try:
                invoice_number = invoice_number_field.value
                customer_name = customer_field.value
                invoice_date = date_field.value
                
                if not invoice_number or not invoice_date:
                    self.show_snack_bar("Заполните обязательные поля")
                    return
                
                conn = sqlite3.connect('computer_store.db')
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO outcome_invoices (invoice_number, customer_name, invoice_date, total_amount)
                    VALUES (?, ?, ?, ?)
                ''', (invoice_number, customer_name, invoice_date, 0))
                conn.commit()
                conn.close()
                
                self.page.close(dialog)
                self.show_outcome()
                self.show_snack_bar("Расходная накладная создана")
            except Exception as ex:
                self.show_snack_bar(f"Ошибка создания накладной: {ex}")
        
        invoice_number_field = ft.TextField(label="Номер накладной*", width=400)
        customer_field = ft.TextField(label="Имя клиента", width=400)
        date_field = ft.TextField(
            label="Дата накладной*", 
            width=400, 
            value=date.today().isoformat(),
            hint_text="ГГГГ-ММ-ДД"
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Создать расходную накладную"),
            content=ft.Container(
                content=ft.Column([
                    invoice_number_field,
                    customer_field,
                    date_field,
                ]),
                width=400
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Сохранить", on_click=save_invoice),
            ]
        )
        self.page.open(dialog)
    
    def show_reports(self):
        """Показать раздел отчетов с красивыми визуальными отчетами"""
        self.main_content.controls.clear()
        self.main_content.controls.append(ft.Text("Отчетность", size=28, weight=ft.FontWeight.BOLD))
        self.main_content.controls.append(ft.Divider())
        
        report_buttons = ft.ResponsiveRow([
            ft.ElevatedButton(
                "Отчет по остаткам",
                icon=ft.Icons.INVENTORY_2,
                on_click=self.generate_stock_report,
                col=6,
                style=ft.ButtonStyle(padding=15)
            ),
            ft.ElevatedButton(
                "Отчет по продажам",
                icon=ft.Icons.BAR_CHART,
                on_click=self.generate_sales_report,
                col=6,
                style=ft.ButtonStyle(padding=15)
            ),
            ft.ElevatedButton(
                "Оборотная ведомость",
                icon=ft.Icons.ANALYTICS,
                on_click=self.generate_turnover_report,
                col=6,
                style=ft.ButtonStyle(padding=15)
            ),
            ft.ElevatedButton(
                "Отчет по поставщикам",
                icon=ft.Icons.PEOPLE,
                on_click=self.generate_suppliers_report,
                col=6,
                style=ft.ButtonStyle(padding=15)
            ),
        ])
        
        self.main_content.controls.append(report_buttons)
        self.page.update()
    
    def generate_stock_report(self, e):
        """Генерация отчета по остаткам с красивым оформлением"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.name, c.name as category, p.quantity, p.min_quantity, p.price,
                       CASE WHEN p.quantity <= p.min_quantity AND p.min_quantity > 0 THEN 1 ELSE 0 END as low_stock
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY low_stock DESC, p.quantity ASC
            ''')
            products = cursor.fetchall()
            conn.close()
            
            # Создаем визуальный отчет
            report_content = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
            
            # Заголовок
            report_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("ОТЧЕТ ПО ОСТАТКАМ ТОВАРОВ", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Дата формирования: {date.today()}", size=14),
                        ft.Divider()
                    ]),
                    padding=10
                )
            )
            
            # Статистика
            total_products = len(products)
            low_stock_count = sum(1 for p in products if p[5] == 1)
            total_value = sum(p[4] * p[2] for p in products)
            
            stats_row = ft.ResponsiveRow([
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(total_products), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                        ft.Text("Всего товаров", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=4
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(low_stock_count), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
                        ft.Text("Низкий запас", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=4
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{total_value:.2f} руб.", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                        ft.Text("Общая стоимость", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=4
                ),
            ])
            
            report_content.controls.append(ft.Container(content=stats_row, padding=10))
            
            # Таблица товаров
            data_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Товар")),
                    ft.DataColumn(ft.Text("Категория")),
                    ft.DataColumn(ft.Text("Остаток")),
                    ft.DataColumn(ft.Text("Мин. запас")),
                    ft.DataColumn(ft.Text("Цена")),
                    ft.DataColumn(ft.Text("Статус")),
                ],
                rows=[]
            )
            
            for product in products:
                status_color = ft.Colors.RED if product[5] == 1 else ft.Colors.GREEN
                status_text = "Низкий запас!" if product[5] == 1 else "В норме"
                
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(product[0])),
                            ft.DataCell(ft.Text(product[1])),
                            ft.DataCell(ft.Text(str(product[2]))),
                            ft.DataCell(ft.Text(str(product[3]))),
                            ft.DataCell(ft.Text(f"{product[4]:.2f} руб.")),
                            ft.DataCell(ft.Text(status_text, color=status_color, weight=ft.FontWeight.BOLD)),
                        ]
                    )
                )
            
            report_content.controls.append(ft.Container(content=data_table, padding=10))
            
            self.show_report_dialog("Отчет по остаткам", report_content)
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка генерации отчета: {ex}")
    
    def generate_sales_report(self, e):
        """Генерация отчета по продажам с красивым оформлением"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT oi.invoice_number, oi.invoice_date, oi.customer_name, oi.total_amount
                FROM outcome_invoices oi
                ORDER BY oi.invoice_date DESC
                LIMIT 20
            ''')
            sales = cursor.fetchall()
            conn.close()
            
            report_content = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
            
            # Заголовок
            report_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("ОТЧЕТ ПО ПРОДАЖАМ", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Дата формирования: {date.today()}", size=14),
                        ft.Divider()
                    ]),
                    padding=10
                )
            )
            
            # Статистика
            total_sales = sum(sale[3] or 0 for sale in sales)
            total_invoices = len(sales)
            
            stats_row = ft.ResponsiveRow([
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(total_invoices), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                        ft.Text("Всего накладных", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=6
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{total_sales:.2f} руб.", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                        ft.Text("Общая сумма", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=6
                ),
            ])
            
            report_content.controls.append(ft.Container(content=stats_row, padding=10))
            
            # Таблица продаж
            if sales:
                data_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Накладная")),
                        ft.DataColumn(ft.Text("Дата")),
                        ft.DataColumn(ft.Text("Клиент")),
                        ft.DataColumn(ft.Text("Сумма")),
                    ],
                    rows=[]
                )
                
                for sale in sales:
                    data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(sale[0])),
                                ft.DataCell(ft.Text(sale[1])),
                                ft.DataCell(ft.Text(sale[2] or "Не указан")),
                                ft.DataCell(ft.Text(f"{sale[3] or 0:.2f} руб.", color=ft.Colors.GREEN_400)),
                            ]
                        )
                    )
                
                report_content.controls.append(ft.Container(content=data_table, padding=10))
            else:
                report_content.controls.append(
                    ft.Container(
                        content=ft.Text("Нет данных о продажах", style=ft.TextStyle(italic=True)),
                        padding=20,
                        alignment=ft.alignment.center
                    )
                )
            
            self.show_report_dialog("Отчет по продажам", report_content)
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка генерации отчета: {ex}")
    
    def generate_turnover_report(self, e):
        """Генерация оборотной ведомости с красивым оформлением"""
        try:
            month_start = date.today().replace(day=1)
            
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            
            # Приход за месяц
            cursor.execute('''
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                FROM income_invoices 
                WHERE invoice_date >= ?
            ''', (month_start.isoformat(),))
            income_data = cursor.fetchone()
            
            # Расход за месяц
            cursor.execute('''
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                FROM outcome_invoices 
                WHERE invoice_date >= ?
            ''', (month_start.isoformat(),))
            outcome_data = cursor.fetchone()
            
            conn.close()
            
            report_content = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
            
            # Заголовок
            report_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("ОБОРОТНАЯ ВЕДОМОСТЬ", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Период: {month_start.strftime('%B %Y')}", size=14),
                        ft.Text(f"Дата формирования: {date.today()}", size=14),
                        ft.Divider()
                    ]),
                    padding=10
                )
            )
            
            # Статистика
            income_count, income_total = income_data
            outcome_count, outcome_total = outcome_data
            turnover = income_total + outcome_total
            
            stats_grid = ft.ResponsiveRow([
                # Приход
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INPUT, size=40, color=ft.Colors.GREEN_400),
                        ft.Text(str(income_count), size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Приходных накладных", size=12),
                        ft.Text(f"{income_total:.2f} руб.", size=16, color=ft.Colors.GREEN_400)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=15,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=6
                ),
                # Расход
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.OUTPUT, size=40, color=ft.Colors.RED_400),
                        ft.Text(str(outcome_count), size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Расходных накладных", size=12),
                        ft.Text(f"{outcome_total:.2f} руб.", size=16, color=ft.Colors.RED_400)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=15,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=6
                ),
                # Оборот
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.AUTORENEW, size=40, color=ft.Colors.BLUE_400),
                        ft.Text(f"{turnover:.2f} руб.", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("Общий оборот", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=15,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=12
                ),
            ])
            
            report_content.controls.append(ft.Container(content=stats_grid, padding=10))
            
            self.show_report_dialog("Оборотная ведомость", report_content)
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка генерации отчета: {ex}")
    
    def generate_suppliers_report(self, e):
        """Генерация отчета по поставщикам с красивым оформлением"""
        try:
            conn = sqlite3.connect('computer_store.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.name, s.contact_person, s.phone, 
                       COUNT(ii.id) as invoice_count,
                       COALESCE(SUM(ii.total_amount), 0) as total_amount
                FROM suppliers s
                LEFT JOIN income_invoices ii ON s.id = ii.supplier_id
                GROUP BY s.id
                ORDER BY total_amount DESC
            ''')
            suppliers = cursor.fetchall()
            conn.close()
            
            report_content = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)
            
            # Заголовок
            report_content.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("ОТЧЕТ ПО ПОСТАВЩИКАМ", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Дата формирования: {date.today()}", size=14),
                        ft.Divider()
                    ]),
                    padding=10
                )
            )
            
            # Статистика
            total_suppliers = len(suppliers)
            total_invoices = sum(s[3] for s in suppliers)
            total_amount = sum(s[4] for s in suppliers)
            
            stats_row = ft.ResponsiveRow([
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(total_suppliers), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400),
                        ft.Text("Всего поставщиков", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=4
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(total_invoices), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400),
                        ft.Text("Всего накладных", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=4
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(f"{total_amount:.2f} руб.", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
                        ft.Text("Общая сумма", size=12)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=10,
                    col=4
                ),
            ])
            
            report_content.controls.append(ft.Container(content=stats_row, padding=10))
            
            # Таблица поставщиков
            if suppliers:
                data_table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Поставщик")),
                        ft.DataColumn(ft.Text("Контакт")),
                        ft.DataColumn(ft.Text("Телефон")),
                        ft.DataColumn(ft.Text("Накладных")),
                        ft.DataColumn(ft.Text("Сумма")),
                    ],
                    rows=[]
                )
                
                for supplier in suppliers:
                    data_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(supplier[0], weight=ft.FontWeight.BOLD)),
                                ft.DataCell(ft.Text(supplier[1] or "-")),
                                ft.DataCell(ft.Text(supplier[2] or "-")),
                                ft.DataCell(ft.Text(str(supplier[3]))),
                                ft.DataCell(ft.Text(f"{supplier[4]:.2f} руб.", color=ft.Colors.GREEN_400)),
                            ]
                        )
                    )
                
                report_content.controls.append(ft.Container(content=data_table, padding=10))
            else:
                report_content.controls.append(
                    ft.Container(
                        content=ft.Text("Нет данных о поставщиках", style=ft.TextStyle(italic=True)),
                        padding=20,
                        alignment=ft.alignment.center
                    )
                )
            
            self.show_report_dialog("Отчет по поставщикам", report_content)
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка генерации отчета: {ex}")
    
    def show_report_dialog(self, title, content):
        """Показать диалог с красивым отчетом"""
        dialog = ft.AlertDialog(
            title=ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=content,
                width=700,
                height=500
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=lambda e: self.page.close(dialog)),
            ]
        )
        self.page.open(dialog)
    
    def show_backup(self):
        """Показать раздел резервного копирования с рабочими кнопками"""
        self.main_content.controls.clear()
        self.main_content.controls.append(ft.Text("Резервное копирование", size=28, weight=ft.FontWeight.BOLD))
        self.main_content.controls.append(ft.Divider())
        
        backup_controls = ft.Column([
            ft.Text("Управление резервными копиями базы данных", size=16),
            ft.ResponsiveRow([
                ft.ElevatedButton(
                    "Создать резервную копию",
                    icon=ft.Icons.BACKUP,
                    on_click=self.create_backup,
                    col=6,
                    style=ft.ButtonStyle(padding=15)
                ),
                ft.ElevatedButton(
                    "Восстановить из копии",
                    icon=ft.Icons.RESTORE,
                    on_click=self.restore_backup,
                    col=6,
                    style=ft.ButtonStyle(padding=15)
                ),
            ])
        ])
        
        self.main_content.controls.append(backup_controls)
        self.page.update()
    
    def create_backup(self, e):
        """Создать резервную копию - РАБОЧАЯ ВЕРСИЯ"""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"computer_store_backup_{timestamp}.db"
            
            shutil.copy2("computer_store.db", backup_file)
            
            self.show_snack_bar(f"Резервная копия создана: {backup_file.name}")
            
        except Exception as ex:
            self.show_snack_bar(f"Ошибка создания резервной копии: {ex}")
    
    def restore_backup(self, e):
        """Восстановить из резервной копии - РАБОЧАЯ ВЕРСИЯ"""
        def restore_selected(e):
            if file_picker.result is not None and file_picker.result.files is not None:
                selected_file = file_picker.result.files[0].path
                try:
                    shutil.copy2(selected_file, "computer_store.db")
                    self.page.close(dialog)
                    self.show_snack_bar("База данных восстановлена из резервной копии")
                except Exception as ex:
                    self.show_snack_bar(f"Ошибка восстановления: {ex}")
        
        file_picker = ft.FilePicker(on_result=restore_selected)
        self.page.overlay.append(file_picker)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Восстановление из резервной копии"),
            content=ft.Text("Выберите файл резервной копии для восстановления:"),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: self.page.close(dialog)),
                ft.ElevatedButton(
                    "Выбрать файл",
                    on_click=lambda _: file_picker.pick_files(
                        allowed_extensions=["db"],
                        dialog_title="Выберите файл резервной копии"
                    )
                ),
            ]
        )
        self.page.open(dialog)
    
    def show_user_info(self, e):
        """Показать информацию о пользователе"""
        if self.current_user:
            self.show_snack_bar(f"Пользователь: {self.current_user['full_name']} ({self.current_user['role']})")
    
    def show_about(self, e):
        """Показать информацию о программе"""
        about_dialog = ft.AlertDialog(
            title=ft.Text("О программе"),
            content=ft.Column([
                ft.Text("АИС 'Компьютерный салон'", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Версия 1.0"),
                ft.Text("Автоматизированная информационная система"),
                ft.Text("для учета компьютерной техники и комплектующих"),
                ft.Divider(),
                ft.Text("Справка доступна по кнопке '?' в правом верхнем углу", style=ft.TextStyle(italic=True))
            ], tight=True),
            actions=[
                ft.TextButton("Справка", on_click=lambda e: self.show_help()),
                ft.TextButton("Закрыть", on_click=lambda e: self.page.close(about_dialog)),
            ],
        )
        self.page.open(about_dialog)

if __name__ == "__main__":
    app = ComputerStoreApp()
    ft.app(target=app.main)