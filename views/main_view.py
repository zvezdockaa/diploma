import customtkinter as ctk
ctk.set_appearance_mode("Light")
from PIL import Image
import os
import datetime
from views.graph_builder import GraphBuilder

# основное окно приложения
class MainView(ctk.CTk):
    def __init__(self, controller, available_countries):
        super().__init__()

        self.controller = controller
        self.available_countries = available_countries
        self.user_models = []  # список пользовательских моделей
        self.headers = []      # список заголовков таблицы
        self.header_widgets = []  # виджеты заголовков
        self.last_notification = ""  # последнее уведомление

        self.title("Оценка совокупной мощи государств")
        self.geometry("1200x600")

    # построение основного интерфейса
    def build_main_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        # выбор страны и года
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(pady=20, padx=20, fill="x")

        label = ctk.CTkLabel(top_frame, text="Выберите страну для расчета:")
        label.pack(side="left", padx=(0, 10))

        self.country_combobox = ctk.CTkComboBox(top_frame, values=self.available_countries, state="readonly", width=400)
        self.country_combobox.pack(side="left")

        year_label = ctk.CTkLabel(top_frame, text="Год:")
        year_label.pack(side="left", padx=(20, 5))

        years = [str(y) for y in range(2000, datetime.datetime.now().year + 1)]
        self.year_combobox = ctk.CTkComboBox(top_frame, values=years, state="readonly", width=100)
        self.year_combobox.set(str(datetime.datetime.now().year))  # текущий год по умолчанию
        self.year_combobox.pack(side="left")

        # кнопки действий
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=20, pady=10, anchor="w")

        ctk.CTkButton(button_frame, text="Добавить страну", command=self.on_add_country).grid(row=0, column=0, padx=10)
        ctk.CTkButton(button_frame, text="Экспорт в Excel", command=self.controller.export_data).grid(row=0, column=1, padx=10)
        ctk.CTkButton(button_frame, text="Добавить модель", command=self.open_formula_builder).grid(row=0, column=2, padx=10)
        ctk.CTkButton(button_frame, text="Построить график", command=self.open_graph_builder).grid(row=0, column=3, padx=10)

        # иконка уведомления
        bell_path = os.path.join(os.path.dirname(__file__), "..", "bell.png")
        if os.path.exists(bell_path):
            image = Image.open(bell_path).resize((24, 24))
            self.bell_icon = ctk.CTkImage(dark_image=image, light_image=image, size=(24, 24))
            self.bell_button = ctk.CTkButton(self, image=self.bell_icon, text="", width=30, height=30,
                                             fg_color="transparent", hover=False,
                                             command=self.toggle_notification_popup)
            self.bell_button.place(relx=0.98, rely=0.02, anchor="ne")

        # область для отображения таблицы
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=1000, height=400)
        self.scrollable_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.build_table_headers()

    # открытие окна построения графика
    def open_graph_builder(self):
        GraphBuilder(self, self.controller)

    # построение заголовков таблицы с кнопками сортировки
    def build_table_headers(self):
        self.headers = ["Страна", "Год", "ВВП (млн USD)", "Военные расходы (млн USD)",
                        "Совокупная мощь по Чин-Лунгу", "Индекс национального потенциала"] + self.user_models
        self.header_widgets.clear()

        for col, header in enumerate(self.headers):
            header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            header_frame.grid(row=0, column=col, padx=10, pady=5, sticky="w")

            label = ctk.CTkLabel(header_frame, text=header, font=("Arial", 12, "bold"))
            label.pack(side="left", padx=(0, 4))

            # кнопки сортировки
            sort_asc = ctk.CTkButton(header_frame, text="▲", width=20, height=20,
                                     fg_color=None, hover_color=None,
                                     command=lambda c=col: self.sort_table(c, ascending=True))
            sort_asc.pack(side="left", padx=(0, 2))

            sort_desc = ctk.CTkButton(header_frame, text="▼", width=20, height=20,
                                      fg_color=None, hover_color=None,
                                      command=lambda c=col: self.sort_table(c, ascending=False))
            sort_desc.pack(side="left")

            self.header_widgets.append(header_frame)

    # добавляет одну строку в таблицу
    def add_table_row(self, row_data):
        row_idx = len(self.scrollable_frame.grid_slaves()) // len(self.headers) + 1

        for col_idx, key in enumerate(self.headers):
            value = row_data.get(key, "")
            fg_color = "#2fa3de" if col_idx > 3 else None
            text_color = "white" if col_idx > 3 else "black"

            # форматирование чисел
            if key in ["ВВП (млн USD)", "Военные расходы (млн USD)"]:
                try:
                    numeric_value = float(value)
                    display_value = f"{numeric_value:,.0f}".replace(",", " ")
                except (ValueError, TypeError):
                    display_value = str(value)
            else:
                display_value = str(value)

            cell = ctk.CTkLabel(self.scrollable_frame, text=display_value, anchor="w",
                                fg_color=fg_color, text_color=text_color, corner_radius=5)
            cell.grid(row=row_idx, column=col_idx, padx=10, pady=5, sticky="w")

    # сортировка таблицы по выбранному столбцу
    def sort_table(self, column_index, ascending=True):
        try:
            self.controller.country_data.sort(
                key=lambda x: float(str(x.get(self.headers[column_index])).replace(",", "")),
                reverse=not ascending
            )
            # перерисовка таблицы после сортировки
            for widget in self.scrollable_frame.winfo_children():
                info = widget.grid_info()
                if int(info["row"]) > 0:
                    widget.destroy()
            for row in self.controller.country_data:
                self.add_table_row(row)
        except Exception as e:
            self.notify(f"Ошибка при сортировке: {e}")

    # вызов уведомления
    def notify(self, message):
        self.last_notification = message
        self.show_popup_notification(message)

    # вывод всплывающего уведомления
    def show_popup_notification(self, message):
        if hasattr(self, 'temp_popup') and self.temp_popup and self.temp_popup.winfo_exists():
            self.temp_popup.destroy()

        self.temp_popup = ctk.CTkToplevel(self)
        self.temp_popup.overrideredirect(True)
        self.temp_popup.attributes("-topmost", True)
        self.temp_popup.geometry("+{}+{}".format(self.winfo_rootx() + self.winfo_width() - 320,
                                                 self.winfo_rooty() + 60))

        label = ctk.CTkLabel(self.temp_popup, text=message, fg_color="orange", text_color="white",
                             corner_radius=8, width=260, height=30)
        label.pack()

        self.after(3000, self.temp_popup.destroy)

    # отображение последнего уведомления по клику
    def toggle_notification_popup(self):
        if hasattr(self, "popup") and self.popup and self.popup.winfo_exists():
            self.popup.destroy()
            self.popup = None
        elif self.last_notification:
            self.popup = ctk.CTkToplevel(self)
            self.popup.title("Уведомление")
            self.popup.geometry("300x100")
            self.popup.attributes("-topmost", True)

            label = ctk.CTkLabel(self.popup, text=self.last_notification, wraplength=280)
            label.pack(padx=10, pady=10)

            ok_button = ctk.CTkButton(self.popup, text="OK", command=self.popup.destroy)
            ok_button.pack(pady=(0, 10))

    # добавление страны в таблицу по кнопке
    def on_add_country(self):
        country_name = self.country_combobox.get()
        selected_year = int(self.year_combobox.get())
        self.controller.add_country(country_name, selected_year)

    # открытие конструктора пользовательских моделей
    def open_formula_builder(self):
        from views.formula_builder_view import FormulaBuilderView
        all_metrics = [
            "ВВП", "Военные расходы", "Экономическая сила", "Военная сила",
            "Критическая масса", "Совокупная мощь по Чин-Лунгу", "ВВП ППС", "ВВП ППС на душу",
            "Население", "Площадь", "Глобальный ВВП", "Глобальные военные расходы",
            "Глобальный ВВП ППС на душу", "Глобальное население",
            "Часть ВР", "Часть ВВП", "Часть ВВП ППС", "Часть населения",
            "Индекс национального потенциала"
        ]

        FormulaBuilderView(self, all_metrics, self.controller.add_user_model)
