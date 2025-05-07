import customtkinter as ctk
import requests
import openpyxl
import pandas as pd
from dict import country_codes
from formula_creator import FormulaBuilder
from PIL import Image
import os

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

military_spending_file = "военные расходы.xlsx"

militarySpending_total = 2443398.80320217  #  в миллионах долларов


# функция для получения данных через API World Bank
def fetch_data_from_world_bank(country_code, indicator, year=2023):
    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator}?format=json&date={year}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if len(data) < 2 or not data[1]:
            return None
        value = data[1][0].get("value")
        return value if value else None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return None

# функция для получения данных о военных расходах
def fetch_military_spending(filename, sheet_name, country):
    try:
        workbook = openpyxl.load_workbook(filename)
        sheet = workbook[sheet_name]
        for row in sheet.iter_rows(values_only=True):
            if str(row[0]).strip().lower() == country.strip().lower():
                spending_str = str(row[1]).strip()
                if spending_str.lower() in ["...", "nan", ""]:
                    return 0, f"Данные о военных расходах для страны '{country}' неизвестны"
                try:
                    spending = float(spending_str.replace(",", ""))
                    return round(spending,5), None
                except ValueError:
                    return 0, f"Ошибка преобразования данных для страны '{country}': невозможно преобразовать '{spending_str}' в число"
        return 0, f"Данные о военных расходах для страны '{country}' неизвестны"
    except Exception as e:
        raise ValueError(f"Не удалось открыть файл: {e}")

# функция для расчета критической Массы
def get_critical_mass(country_code: str, year: int = 2023) -> float:
    # индикаторы: население и площадь
    POPULATION = 'SP.POP.TOTL'
    AREA = 'AG.SRF.TOTL.K2'

    #  данные по стране
    country_population = fetch_data_from_world_bank(country_code, POPULATION, year)
    country_area = fetch_data_from_world_bank(country_code, AREA, year)

    #  данные по миру
    world_population = fetch_data_from_world_bank("WLD", POPULATION, year)
    world_area = fetch_data_from_world_bank("WLD", AREA, year)

    # если каких-то данных нет, замена на 0
    country_population = country_population if country_population else 0
    country_area = country_area if country_area else 0
    world_population = world_population if world_population else 1
    world_area = world_area if world_area else 1

    # критическая масса по формуле
    critical_mass = (country_population / world_population) * 100 + (country_area / world_area) * 100
    return round(critical_mass, 2)

# функция для расчета показателей
def calculate_metrics(selected_country):
    code = country_codes.get(selected_country)
    results = {}

    gdp_current = fetch_data_from_world_bank(code, "NY.GDP.MKTP.CD")
    results["ВВП"] = round(gdp_current / 1_000_000, 2) if gdp_current else 0

    military_spending, error_message = fetch_military_spending(military_spending_file, "Current US$", selected_country)
    results["Военные расходы"] = military_spending if military_spending else 0

    world_gdp_data = fetch_data_from_world_bank("WLD", "NY.GDP.MKTP.CD")
    economic_strength = (gdp_current / world_gdp_data) * 200 if gdp_current and world_gdp_data else 0
    results["Экономическая сила"] = round(economic_strength, 2)

    military_strength = (military_spending / militarySpending_total) * 200 if military_spending > 0 else 0
    results["Военная сила"] = round(military_strength, 2)

    critical_mass = get_critical_mass(code)
    results["Критическая масса"] = critical_mass

    power_chin_lung = (results["Критическая масса"] + economic_strength + military_strength) / 3
    results["Совокупная мощь по Чин-Лунгу"] = round(power_chin_lung, 2)

    global_gdp = world_gdp_data
    global_gdp_ppp_per_capita = fetch_data_from_world_bank("WLD", "NY.GDP.PCAP.PP.CD")
    global_population = fetch_data_from_world_bank("WLD", "SP.POP.TOTL")
    country_gdp_ppp = fetch_data_from_world_bank(code, "NY.GDP.MKTP.PP.CD")
    country_gdp_ppp_per_capita = fetch_data_from_world_bank(code, "NY.GDP.PCAP.PP.CD")
    country_population = fetch_data_from_world_bank(code, "SP.POP.TOTL")

    results["Население"] = country_population or 0
    results["ВВП ППС"] = country_gdp_ppp or 0
    results["ВВП ППС на душу"] = country_gdp_ppp_per_capita or 0
    results["Общемировой ВВП"] = global_gdp or 0
    results["Общемировые военные расходы"] = militarySpending_total * 1_000_000
    results["Общемировое население"] = global_population or 1
    results["Общемировой ВВП ППС на душу"] = global_gdp_ppp_per_capita or 1

    military_part = (results["Военные расходы"] * 1_000_000 / results["Глобальные военные расходы"]) * 0.29
    gdp_part = ((gdp_current * results["ВВП ППС на душу"]) / (global_gdp * results["Глобальный ВВП ППС на душу"])) * 0.1 if global_gdp and global_gdp_ppp_per_capita else 0
    gdp_ppp_part = (results["ВВП ППС"] / global_gdp) * 0.35 if global_gdp else 0
    population_part = (results["Население"] / results["Глобальное население"]) * 0.26 if global_population else 0

    results["Часть ВР"] = round(military_part, 6)
    results["Часть ВВП"] = round(gdp_part, 6)
    results["Часть ВВП ППС"] = round(gdp_ppp_part, 6)
    results["Часть населения"] = round(population_part, 6)

    national_potential_index = military_part + gdp_part + gdp_ppp_part + population_part
    results["Индекс национального потенциала"] = round(national_potential_index, 4)

    return results, error_message

# функция для экспорта расчетов в Excel
def export_to_excel(data):

    try:
        # датафрейм из списка словарей
        df = pd.DataFrame(data)
        file_name = "exported_data.xlsx"
        df.to_excel(file_name, index=False)

        print(f"Данные успешно экспортированы в файл '{file_name}'")
    except Exception as e:
        print(f"Ошибка при экспорте данных: {e}")

#загрузка модели пользователя
def evaluate_custom_formula(formula: str, data: dict) -> float:
    try:
        safe_data = {k.replace(" ", "_"): v for k, v in data.items()}
        code = compile(formula.replace(" ", "_"), "<string>", "eval")
        return round(eval(code, {"__builtins__": {}}, safe_data), 4)
    except Exception:
        return 0.0

#основной класс приложения
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Оценка совокупной мощи государств")
        self.geometry("1200x600")

        self.added_countries_data = []
        self.user_models = {}
        self.last_notification = ""

        self.show_main_screen()


    #отображение на главном экране
    def show_main_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        selection_frame = ctk.CTkFrame(self)
        selection_frame.pack(pady=20, padx=20, fill="x")

        self.country_label = ctk.CTkLabel(selection_frame, text="Выберите страну для расчета:")
        self.country_label.pack(side="left", padx=(0, 10))

        self.country_combobox = ctk.CTkComboBox(selection_frame, values=list(country_codes.keys()), state="readonly",
                                                width=400)
        self.country_combobox.pack(side="left")

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(padx=20, pady=10, anchor="w")

        self.add_button = ctk.CTkButton(button_frame, text="Добавить страну", command=self.add_country)
        self.add_button.grid(row=0, column=0, padx=10)

        self.export_button = ctk.CTkButton(button_frame, text="Экспорт в Excel", command=self.export_data)
        self.export_button.grid(row=0, column=1, padx=10)

        self.model_button = ctk.CTkButton(button_frame, text="Добавить модель", command=self.open_model_builder)
        self.model_button.grid(row=0, column=2, padx=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=900, height=400)
        self.scrollable_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # колокольчик
        bell_path = os.path.join(os.path.dirname(__file__), "bell.png")
        if os.path.exists(bell_path):
            image = Image.open(bell_path).resize((24, 24))
            self.bell_icon = ctk.CTkImage(dark_image=image, light_image=image, size=(24, 24))
            self.bell_button = ctk.CTkButton(
                self, image=self.bell_icon, text="", width=30, height=30,
                fg_color="transparent", hover=False, command=self.toggle_notification_popup
            )
            self.bell_button.place(relx=0.98, rely=0.02, anchor="ne")

        self.notification_popup = None
        self.build_table_headers()


    # отображение уведомлений
    def toggle_notification_popup(self):
        if self.notification_popup and self.notification_popup.winfo_exists():
            self.notification_popup.destroy()
            self.notification_popup = None
        elif self.last_notification:
            self.notification_popup = ctk.CTkToplevel(self)
            self.notification_popup.title("Уведомление")
            self.notification_popup.geometry("300x100")
            self.notification_popup.attributes("-topmost", True)

            label = ctk.CTkLabel(self.notification_popup, text=self.last_notification, wraplength=280)
            label.pack(padx=10, pady=10)

            ok_button = ctk.CTkButton(self.notification_popup, text="OK", command=self.notification_popup.destroy)
            ok_button.pack(pady=(0, 10))

    def show_notification(self, message):
        self.last_notification = message
        print(f"Уведомление: {message}")

    #заголовки таблицы
    def build_table_headers(self):
        headers = ["Страна", "ВВП (млн USD)", "Военные расходы (млн USD)", "Совокупная мощь по Чин-Лунгу", "Индекс национального потенциала"]
        headers += list(self.user_models.keys())
        self.header_widgets = []

        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.scrollable_frame)
            header_frame.grid(row=0, column=col, padx=10, pady=5, sticky="w")

            label = ctk.CTkLabel(header_frame, text=header, font=("Arial", 12, "bold"), anchor="w")
            label.pack(side="left")

            if col > 0:
                sort_asc_button = ctk.CTkButton(header_frame, text="▲", width=20, height=20,
                                                fg_color=self.add_button.cget("fg_color"),
                                                hover_color=self.add_button.cget("hover_color"),
                                                command=lambda c=col: self.sort_table(c, ascending=True))
                sort_asc_button.pack(side="left", padx=(5, 0))

                sort_desc_button = ctk.CTkButton(header_frame, text="▼", width=20, height=20,
                                                 fg_color=self.add_button.cget("fg_color"),
                                                 hover_color=self.add_button.cget("hover_color")                                                 ,
                                                 command=lambda c=col: self.sort_table(c, ascending=False))
                sort_desc_button.pack(side="left")

            self.header_widgets.append(header_frame)

    # сортировка показателей в таблице
    def sort_table(self, column_index, ascending=True):
        try:
            self.added_countries_data.sort(
                key=lambda x: float(x[list(x.keys())[column_index]].replace(",", "")
                                    if isinstance(x[list(x.keys())[column_index]], str)
                                    else x[list(x.keys())[column_index]]),
                reverse=not ascending
            )
            self.redraw_table()
        except Exception as e:
            print(f"Ошибка при сортировке: {e}")

    # добавление страны для расчета
    def add_country(self):
        selected_country = self.country_combobox.get()
        if not selected_country:
            print("Страна не выбрана!")
            return

        if selected_country in [d["Страна"] for d in self.added_countries_data]:
            print(f"Страна '{selected_country}' уже добавлена!")
            return

        metrics, error = calculate_metrics(selected_country)
        country_data = {
            "Страна": selected_country,
            "ВВП (млн USD)": metrics["ВВП"],
            "Военные расходы (млн USD)": metrics["Военные расходы"],
            "Совокупная мощь по Чин-Лунгу": metrics["Совокупная мощь по Чин-Лунгу"],
            "Индекс национального потенциала": metrics["Индекс национального потенциала"]
        }

        for model_name, formula in self.user_models.items():
            value = evaluate_custom_formula(formula, metrics)
            country_data[model_name] = value

        self.added_countries_data.append(country_data)
        self.redraw_table()
        if error:
            self.show_notification(error)

    # экспорт в эксель
    def export_data(self):
        if not self.added_countries_data:
            print("Нет данных для экспорта!")
            return
        export_to_excel(self.added_countries_data)

    # новая отрисовка таблицы
    def redraw_table(self):
        for widget in self.scrollable_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget not in self.header_widgets:
                widget.destroy()

        for row_idx, data in enumerate(self.added_countries_data, start=1):
            row_data = [
                data.get("Страна", ""),
                "{:,}".format(data.get("ВВП (млн USD)", 0)),
                "{:,}".format(data.get("Военные расходы (млн USD)", 0)),
                str(data.get("Совокупная мощь по Чин-Лунгу", 0)),
                str(data.get("Индекс национального потенциала", 0))
            ]
            for model_name in self.user_models:
                row_data.append(str(data.get(model_name, 0)))

            for col, value in enumerate(row_data):
                fg_color = None
                text_color = "black"

                if col >= 3:
                    fg_color = "#2fa3de"
                    text_color = "white"

                value_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text=value,
                    anchor="w",
                    fg_color=fg_color,
                    text_color=text_color,
                    corner_radius=5
                )
                value_label.grid(row=row_idx, column=col, padx=10, pady=5, sticky="w")

    #открытие конструктора для пользовательских моделей
    def open_model_builder(self):
        full_metrics = [
            "ВВП", "Военные расходы", "Экономическая сила", "Военная сила", "Критическая масса",
            "Совокупная мощь по Чин-Лунгу", "Индекс национального потенциала", "Население", "ВВП ППС", "ВВП ППС на душу",
            "Общемировой ВВП", "Общемировые военные расходы", "Общемировое население", "Общемировой ВВП ППС на душу",
            "Часть ВР", "Часть ВВП", "Часть ВВП ППС", "Часть населения"
        ]
        FormulaBuilder(self, full_metrics, self.add_user_model)

    # добавление пользовательской модели в таблицу
    def add_user_model(self, name, formula):
        if name in self.user_models:
            print(f"Модель '{name}' уже существует!")
            return

        self.user_models[name] = formula
        self.build_table_headers()
        for row in self.added_countries_data:
            base_metrics, _ = calculate_metrics(row["Страна"])
            row[name] = evaluate_custom_formula(formula, base_metrics)
        self.redraw_table()


if __name__ == "__main__":
    app = App()
    app.mainloop()