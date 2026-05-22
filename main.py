import customtkinter as ctk
from datetime import datetime, timedelta
from database import (
    check_user, register_user, get_prediction, update_user_info,
    get_all_users, delete_user, update_user, get_all_predictions,
    update_prediction, add_prediction
)
import sys
import os
from tkinter import messagebox

# Настройка DPI для Windows
if os.name == 'nt':
    from ctypes import windll

    try:
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

# Админские данные
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# Определение знака зодиака по дате рождения
def get_zodiac_sign(day, month):
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Овен"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Телец"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Близнецы"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Рак"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Лев"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Дева"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Весы"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Скорпион"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Стрелец"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Козерог"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Водолей"
    else:
        return "Рыбы"


# Китайский зодиак по году рождения
def get_chinese_zodiac(year):
    zodiacs = [
        "Крысы", "Быка", "Тигра", "Кролика", "Дракона", "Змеи",
        "Лошади", "Козы", "Обезьяны", "Петуха", "Собаки", "Свиньи"
    ]
    return zodiacs[(year - 4) % 12]


from tkinter import ttk



class AdminPanel(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("🔧 Панель администратора")
        self.geometry("1000x700")
        self.resizable(True, True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self._create_widgets()
        self._load_data()

    def _create_widgets(self):
        # Вкладки
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка пользователей
        self.users_tab = self.tabview.add("Пользователи")
        self._create_users_tab()

        # Вкладка предсказаний
        self.predictions_tab = self.tabview.add("Предсказания")
        self._create_predictions_tab()

    def _create_users_tab(self):
        # Список пользователей
        self.users_frame = ctk.CTkFrame(self.users_tab)
        self.users_frame.pack(fill="both", expand=True, padx=10, pady=10)


        self.users_tree = ttk.Treeview(self.users_frame, columns=("username", "birth_date", "about"), show="headings")
        self.users_tree.heading("username", text="Логин")
        self.users_tree.heading("birth_date", text="Дата рождения")
        self.users_tree.heading("about", text="О себе")

        # Настройка стиля для Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#2a2d2e",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])

        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading",
                  background=[('active', '#3484F0')])

        self.users_tree.pack(fill="both", expand=True)

        # Кнопки управления пользователями
        buttons_frame = ctk.CTkFrame(self.users_tab)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            buttons_frame,
            text="Обновить список",
            command=self._load_users,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Удалить пользователя",
            command=self._delete_user,
            width=150,
            fg_color="#d9534f"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Редактировать",
            command=self._edit_user_dialog,
            width=150
        ).pack(side="left", padx=5)

    def _create_predictions_tab(self):
        # Список предсказаний
        self.predictions_frame = ctk.CTkFrame(self.predictions_tab)
        self.predictions_frame.pack(fill="both", expand=True, padx=10, pady=10)


        self.predictions_tree = ttk.Treeview(self.predictions_frame,
                                             columns=("zodiac_sign", "week_start", "prediction"),
                                             show="headings")
        self.predictions_tree.heading("zodiac_sign", text="Знак зодиака")
        self.predictions_tree.heading("week_start", text="Неделя")
        self.predictions_tree.heading("prediction", text="Предсказание")
        self.predictions_tree.pack(fill="both", expand=True)

        # Кнопки управления предсказаниями
        buttons_frame = ctk.CTkFrame(self.predictions_tab)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            buttons_frame,
            text="Обновить список",
            command=self._load_predictions,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Редактировать",
            command=self._edit_prediction_dialog,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Добавить на след. неделю",
            command=self._add_prediction_dialog,
            width=200
        ).pack(side="left", padx=5)

    def _load_data(self):
        self._load_users()
        self._load_predictions()

    def _load_users(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        users = get_all_users()
        for user in users:
            self.users_tree.insert("", "end", values=(
                user["username"],
                user["birth_date"],
                user.get("about", "")
            ))

    def _load_predictions(self):
        for item in self.predictions_tree.get_children():
            self.predictions_tree.delete(item)

        predictions = get_all_predictions()
        for pred in predictions:
            self.predictions_tree.insert("", "end", values=(
                pred["zodiac_sign"],
                pred["week_start"],
                pred["prediction"]
            ))

    def _delete_user(self):
        selected = self.users_tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя для удаления")
            return

        username = self.users_tree.item(selected)["values"][0]
        if username == ADMIN_USERNAME:
            messagebox.showwarning("Ошибка", "Нельзя удалить администратора")
            return

        if messagebox.askyesno("Подтверждение", f"Удалить пользователя {username}?"):
            if delete_user(username):
                self._load_users()
                messagebox.showinfo("Успех", "Пользователь удален")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить пользователя")

    def _edit_user_dialog(self):
        selected = self.users_tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите пользователя для редактирования")
            return

        values = self.users_tree.item(selected)["values"]
        username = values[0]
        birth_date = values[1]
        about = values[2] if len(values) > 2 else ""

        dialog = ctk.CTkToplevel(self)
        dialog.title("Редактирование пользователя")
        dialog.geometry("500x400")
        dialog.resizable(False, False)

        ctk.CTkLabel(
            dialog,
            text=f"Редактирование: {username}",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # Дата рождения
        birth_frame = ctk.CTkFrame(dialog)
        birth_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            birth_frame,
            text="Дата рождения (ДД.ММ.ГГГГ):",
            font=("Arial", 12)
        ).pack(side="left")

        self.birth_entry = ctk.CTkEntry(
            birth_frame,
            width=150,
            font=("Arial", 12)
        )
        self.birth_entry.insert(0, birth_date)
        self.birth_entry.pack(side="left", padx=10)

        # О себе
        ctk.CTkLabel(
            dialog,
            text="О себе:",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.about_text = ctk.CTkTextbox(
            dialog,
            height=150,
            font=("Arial", 12),
            wrap="word"
        )
        self.about_text.pack(fill="x", padx=20, pady=5)
        self.about_text.insert("1.0", about)

        # Кнопки
        buttons_frame = ctk.CTkFrame(dialog)
        buttons_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            buttons_frame,
            text="Сохранить",
            command=lambda: self._save_user_changes(username, dialog),
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            command=dialog.destroy,
            width=150,
            fg_color="#6c757d"
        ).pack(side="left", padx=5)

    def _save_user_changes(self, username, dialog):
        birth_date = self.birth_entry.get()
        about = self.about_text.get("1.0", "end-1c")

        try:
            day, month, year = map(int, birth_date.split('.'))
            if not (1 <= day <= 31) or not (1 <= month <= 12) or year < 1900:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Некорректная дата рождения")
            return

        if update_user(username, birth_date, about):
            messagebox.showinfo("Успех", "Изменения сохранены")
            self._load_users()
            dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить изменения")

    def _edit_prediction_dialog(self):
        selected = self.predictions_tree.focus()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите предсказание для редактирования")
            return

        values = self.predictions_tree.item(selected)["values"]
        zodiac_sign = values[0]
        week_start = values[1]
        prediction = values[2]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Редактирование предсказания")
        dialog.geometry("600x400")
        dialog.resizable(False, False)

        ctk.CTkLabel(
            dialog,
            text=f"Редактирование для {zodiac_sign} ({week_start})",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # Предсказание
        ctk.CTkLabel(
            dialog,
            text="Текст предсказания:",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.prediction_text = ctk.CTkTextbox(
            dialog,
            height=200,
            font=("Arial", 12),
            wrap="word"
        )
        self.prediction_text.pack(fill="both", padx=20, pady=5, expand=True)
        self.prediction_text.insert("1.0", prediction)

        # Кнопки
        buttons_frame = ctk.CTkFrame(dialog)
        buttons_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            buttons_frame,
            text="Сохранить",
            command=lambda: self._save_prediction_changes(zodiac_sign, week_start, dialog),
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            command=dialog.destroy,
            width=150,
            fg_color="#6c757d"
        ).pack(side="left", padx=5)

    def _save_prediction_changes(self, zodiac_sign, week_start, dialog):
        prediction = self.prediction_text.get("1.0", "end-1c")

        if update_prediction(zodiac_sign, week_start, prediction):
            messagebox.showinfo("Успех", "Предсказание обновлено")
            self._load_predictions()
            dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить предсказание")

    def _add_prediction_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Добавление предсказания")
        dialog.geometry("600x500")
        dialog.resizable(False, False)

        ctk.CTkLabel(
            dialog,
            text="Добавить предсказание на следующую неделю",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        # Выбор знака зодиака
        zodiac_frame = ctk.CTkFrame(dialog)
        zodiac_frame.pack(fill="x", padx=20, pady=5)

        ctk.CTkLabel(
            zodiac_frame,
            text="Знак зодиака:",
            font=("Arial", 12)
        ).pack(side="left")

        self.new_zodiac_combo = ctk.CTkComboBox(
            zodiac_frame,
            values=[
                "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
                "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
            ],
            width=150,
            font=("Arial", 12)
        )
        self.new_zodiac_combo.pack(side="left", padx=10)

        # Дата следующей недели
        next_week = (datetime.now() + timedelta(days=7 - datetime.now().weekday())).strftime("%Y-%m-%d")
        ctk.CTkLabel(
            dialog,
            text=f"Неделя: {next_week}",
            font=("Arial", 12)
        ).pack(pady=5)

        # Текст предсказания
        ctk.CTkLabel(
            dialog,
            text="Текст предсказания:",
            font=("Arial", 12, "bold")
        ).pack(pady=5)

        self.new_prediction_text = ctk.CTkTextbox(
            dialog,
            height=200,
            font=("Arial", 12),
            wrap="word"
        )
        self.new_prediction_text.pack(fill="both", padx=20, pady=5, expand=True)

        # Кнопки
        buttons_frame = ctk.CTkFrame(dialog)
        buttons_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            buttons_frame,
            text="Добавить",
            command=lambda: self._add_new_prediction(next_week, dialog),
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            command=dialog.destroy,
            width=150,
            fg_color="#6c757d"
        ).pack(side="left", padx=5)

    def _add_new_prediction(self, week_start, dialog):
        zodiac_sign = self.new_zodiac_combo.get()
        prediction = self.new_prediction_text.get("1.0", "end-1c")

        if not zodiac_sign:
            messagebox.showwarning("Ошибка", "Выберите знак зодиака")
            return

        if not prediction.strip():
            messagebox.showwarning("Ошибка", "Введите текст предсказания")
            return

        if add_prediction(zodiac_sign, week_start, prediction):
            messagebox.showinfo("Успех", "Предсказание добавлено")
            self._load_predictions()
            dialog.destroy()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить предсказание")

    def on_close(self):
        self.destroy()


class HoroscopeApp:
    def __init__(self, master, user_data):
        self.master = master
        self.user_data = user_data
        self.window = ctk.CTkToplevel(master)
        self.window.title("✨ Гороскоп")
        self.window.geometry("800x600")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.container = ctk.CTkFrame(self.window)
        self.container.pack(fill="both", expand=True)

        self._create_personal_frame()
        self._create_curiosity_frame()
        self._create_profile_frame()

        self.show_personal_frame()
        self.center_window()

    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"+{x}+{y}")

    def _create_personal_frame(self):
        self.personal_frame = ctk.CTkFrame(self.container)

        ctk.CTkLabel(
            self.personal_frame,
            text="Ваш персональный гороскоп",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        info_frame = ctk.CTkFrame(self.personal_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=10)

        if self.user_data.get("birth_date"):
            day, month, year = map(int, self.user_data["birth_date"].split('.'))

            zodiac_info = f"Ваш знак: {self.user_data['zodiac_sign']}"
            ctk.CTkLabel(
                info_frame,
                text=zodiac_info,
                font=("Arial", 14, "bold")
            ).pack(side="left", padx=20)

            chinese_zodiac = get_chinese_zodiac(year)
            ctk.CTkLabel(
                info_frame,
                text=f"Год {chinese_zodiac}",
                font=("Arial", 14, "bold")
            ).pack(side="right", padx=20)

        buttons_frame = ctk.CTkFrame(self.personal_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)

        ctk.CTkButton(
            buttons_frame,
            text="Узнать о других знаках",
            command=self.show_curiosity_frame,
            width=200,
            font=("Arial", 14)
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            buttons_frame,
            text="Личный кабинет",
            command=self.show_profile_frame,
            width=200,
            font=("Arial", 14)
        ).pack(side="left", padx=10)

        # Кнопка админ-панели (только для админа)
        if self.user_data["username"] == ADMIN_USERNAME:
            ctk.CTkButton(
                buttons_frame,
                text="Админ-панель",
                command=self._open_admin_panel,
                width=200,
                font=("Arial", 14),
                fg_color="#5bc0de"
            ).pack(side="left", padx=10)

        self.personal_prediction_frame = ctk.CTkFrame(self.personal_frame)
        self.personal_prediction_frame.pack(fill="both", expand=True, pady=15, padx=10)

        ctk.CTkLabel(
            self.personal_prediction_frame,
            text="Ваше персональное предсказание:",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.personal_prediction_label = ctk.CTkLabel(
            self.personal_prediction_frame,
            text="",
            wraplength=700,
            font=("Arial", 14),
            justify="center"
        )
        self.personal_prediction_label.pack(pady=20, padx=20)

        if self.user_data.get("zodiac_sign"):
            self._show_personal_prediction(self.user_data["zodiac_sign"])

    def _open_admin_panel(self):
        AdminPanel(self.window)

    def _create_curiosity_frame(self):
        self.curiosity_frame = ctk.CTkFrame(self.container)

        ctk.CTkLabel(
            self.curiosity_frame,
            text="Гороскоп для других знаков",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        ctk.CTkButton(
            self.curiosity_frame,
            text="← Назад к персональному гороскопу",
            command=self.show_personal_frame,
            width=250,
            font=("Arial", 14)
        ).pack(pady=10)

        zodiac_frame = ctk.CTkFrame(self.curiosity_frame, fg_color="transparent")
        zodiac_frame.pack(pady=10)

        ctk.CTkLabel(
            zodiac_frame,
            text="Выберите знак зодиака:",
            font=("Arial", 14)
        ).pack(side="left", padx=10)

        self.zodiac_combo = ctk.CTkComboBox(
            zodiac_frame,
            values=[
                "Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева",
                "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"
            ],
            width=150,
            font=("Arial", 14)
        )
        self.zodiac_combo.pack(side="left", padx=10)

        ctk.CTkButton(
            zodiac_frame,
            text="Показать",
            command=self._show_curiosity_prediction,
            width=100,
            font=("Arial", 14)
        ).pack(side="left", padx=10)

        self.curiosity_prediction_frame = ctk.CTkFrame(self.curiosity_frame)
        self.curiosity_prediction_frame.pack(fill="both", expand=True, pady=15, padx=10)

        self.curiosity_prediction_label = ctk.CTkLabel(
            self.curiosity_prediction_frame,
            text="",
            wraplength=650,
            font=("Arial", 14),
            justify="center"
        )
        self.curiosity_prediction_label.pack(pady=20, padx=20)

    def _create_profile_frame(self):
        self.profile_frame = ctk.CTkFrame(self.container)

        ctk.CTkLabel(
            self.profile_frame,
            text="Личный кабинет",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        ctk.CTkButton(
            self.profile_frame,
            text="← Назад к персональному гороскопу",
            command=self.show_personal_frame,
            width=250,
            font=("Arial", 14)
        ).pack(pady=10)

        info_frame = ctk.CTkFrame(self.profile_frame)
        info_frame.pack(fill="x", pady=10, padx=20)

        if self.user_data.get("birth_date"):
            day, month, year = map(int, self.user_data["birth_date"].split('.'))

            ctk.CTkLabel(
                info_frame,
                text=f"Дата рождения: {day}.{month}.{year}",
                font=("Arial", 14)
            ).pack(pady=5)

            ctk.CTkLabel(
                info_frame,
                text=f"Знак зодиака: {self.user_data['zodiac_sign']}",
                font=("Arial", 14)
            ).pack(pady=5)

            chinese_zodiac = get_chinese_zodiac(year)
            ctk.CTkLabel(
                info_frame,
                text=f"Год {chinese_zodiac} по китайскому календарю",
                font=("Arial", 14)
            ).pack(pady=5)

        about_frame = ctk.CTkFrame(self.profile_frame)
        about_frame.pack(fill="x", pady=20, padx=20)

        ctk.CTkLabel(
            about_frame,
            text="О себе:",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        self.about_text = ctk.CTkTextbox(
            about_frame,
            height=100,
            font=("Arial", 12),
            wrap="word"
        )
        self.about_text.pack(fill="x", padx=10, pady=5)

        if self.user_data.get("about"):
            self.about_text.insert("1.0", self.user_data["about"])

        ctk.CTkButton(
            about_frame,
            text="Сохранить",
            command=self._save_profile_info,
            width=150,
            font=("Arial", 14)
        ).pack(pady=10)

    def _save_profile_info(self):
        about_text = self.about_text.get("1.0", "end-1c")
        if update_user_info(self.user_data["username"], about_text):
            self.user_data["about"] = about_text
            ctk.CTkLabel(
                self.profile_frame,
                text="Изменения сохранены!",
                text_color="green",
                font=("Arial", 12)
            ).pack(pady=5)
        else:
            ctk.CTkLabel(
                self.profile_frame,
                text="Ошибка сохранения!",
                text_color="red",
                font=("Arial", 12)
            ).pack(pady=5)

    def show_personal_frame(self):
        self.curiosity_frame.pack_forget()
        self.profile_frame.pack_forget()
        self.personal_frame.pack(fill="both", expand=True)

    def show_curiosity_frame(self):
        self.personal_frame.pack_forget()
        self.profile_frame.pack_forget()
        self.curiosity_frame.pack(fill="both", expand=True)

    def show_profile_frame(self):
        self.personal_frame.pack_forget()
        self.curiosity_frame.pack_forget()
        self.profile_frame.pack(fill="both", expand=True)

    def _show_personal_prediction(self, zodiac_sign):
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        prediction = get_prediction(zodiac_sign, week_start)
        self.personal_prediction_label.configure(text=prediction)

    def _show_curiosity_prediction(self):
        zodiac_sign = self.zodiac_combo.get()
        if not zodiac_sign:
            return

        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")
        prediction = get_prediction(zodiac_sign, week_start)
        self.curiosity_prediction_label.configure(text=prediction)

    def on_close(self):
        self.window.destroy()
        self.master.deiconify()


class AuthWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔐 Аутентификация")
        self.geometry("500x500")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._create_auth_interface()
        self._center_window()
        self.protocol("WM_DELETE_WINDOW", self._safe_exit)

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def _create_auth_interface(self):
        self.auth_mode = ctk.StringVar(value="login")
        self.user_data = {"birth_date": None, "zodiac_sign": None, "username": None, "about": ""}

        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(
            frame,
            text="Добро пожаловать!",
            font=("Arial", 20, "bold")
        ).pack(pady=12)

        ctk.CTkRadioButton(
            frame,
            text="Вход",
            variable=self.auth_mode,
            value="login",
            font=("Arial", 14)
        ).pack(pady=5)

        ctk.CTkRadioButton(
            frame,
            text="Регистрация",
            variable=self.auth_mode,
            value="register",
            font=("Arial", 14)
        ).pack(pady=5)

        self.username_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Логин",
            width=200,
            font=("Arial", 14)
        )
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Пароль",
            show="*",
            width=200,
            font=("Arial", 14)
        )
        self.password_entry.pack(pady=8)

        self.birth_frame = ctk.CTkFrame(frame, fg_color="transparent")

        self.birth_day = ctk.CTkEntry(
            self.birth_frame,
            placeholder_text="День",
            width=60,
            font=("Arial", 14)
        )
        self.birth_day.pack(side="left", padx=5)

        self.birth_month = ctk.CTkEntry(
            self.birth_frame,
            placeholder_text="Месяц",
            width=60,
            font=("Arial", 14)
        )
        self.birth_month.pack(side="left", padx=5)

        self.birth_year = ctk.CTkEntry(
            self.birth_frame,
            placeholder_text="Год",
            width=80,
            font=("Arial", 14)
        )
        self.birth_year.pack(side="left", padx=5)

        self.birth_frame.pack_forget()

        ctk.CTkButton(
            frame,
            text="Продолжить",
            command=self._handle_auth,
            width=200,
            font=("Arial", 14, "bold")
        ).pack(pady=20)

        self.error_label = ctk.CTkLabel(
            frame,
            text="",
            text_color="red",
            font=("Arial", 12)
        )
        self.error_label.pack()

        self.auth_mode.trace_add("write", self._toggle_birth_field)

    def _toggle_birth_field(self, *args):
        if self.auth_mode.get() == "register":
            self.birth_frame.pack(pady=8)
        else:
            self.birth_frame.pack_forget()

    def _handle_auth(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="Заполните все поля!")
            return

        if self.auth_mode.get() == "login":
            # Проверка на админа
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                self.user_data = {
                    "username": ADMIN_USERNAME,
                    "birth_date": "01.01.2000",
                    "zodiac_sign": "Козерог",
                    "about": "Администратор системы"
                }
                self._open_horoscope_app()
                return

            success, user_info = check_user(username, password)
            if success:
                self.user_data["username"] = username
                self.user_data["birth_date"] = user_info["birth_date"]
                self.user_data["about"] = user_info.get("about", "")

                if user_info["birth_date"]:
                    day, month, year = map(int, user_info["birth_date"].split('.'))
                    self.user_data["zodiac_sign"] = get_zodiac_sign(day, month)

                self._open_horoscope_app()
            else:
                self.error_label.configure(text="Неверный логин или пароль!")
        else:
            try:
                day = int(self.birth_day.get().strip())
                month = int(self.birth_month.get().strip())
                year = int(self.birth_year.get().strip())

                if not (1 <= day <= 31) or not (1 <= month <= 12) or year < 1900 or year > datetime.now().year:
                    raise ValueError

                birth_date = f"{day}.{month}.{year}"
            except:
                self.error_label.configure(text="Введите корректную дату рождения!")
                return

            if register_user(username, password, birth_date):
                self.user_data["username"] = username
                self.user_data["birth_date"] = birth_date
                day, month, year = map(int, birth_date.split('.'))
                self.user_data["zodiac_sign"] = get_zodiac_sign(day, month)
                self.error_label.configure(
                    text="Регистрация успешна! Теперь войдите.",
                    text_color="green"
                )
                self.auth_mode.set("login")
            else:
                self.error_label.configure(text="Логин уже занят!")

    def _open_horoscope_app(self):
        self.withdraw()
        app = HoroscopeApp(self, self.user_data)

    def _safe_exit(self):
        self.quit()
        self.destroy()


if __name__ == "__main__":
    try:
        if os.name == 'nt':
            from ctypes import windll

            try:
                windll.user32.SetProcessDPIAware()
            except:
                pass

        auth_app = AuthWindow()
        auth_app.mainloop()
    except Exception as e:
        print(f"Ошибка при запуске: {e}")
        sys.exit(1)