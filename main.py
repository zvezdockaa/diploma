import customtkinter as ctk
import requests
import openpyxl
from dict import country_codes


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
        return value/1000000 if value else None
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
                    return spending, None
                except ValueError:
                    return 0, f"Ошибка преобразования данных для страны '{country}': невозможно преобразовать '{spending_str}' в число"
        return 0, f"Данные о военных расходах для страны '{country}' неизвестны"
    except Exception as e:
        raise ValueError(f"Не удалось открыть файл: {e}")

# функция для расчета критической Массы
def get_critical_mass(country_code: str, year: int = 2023) -> float:
    # индикаторы
    POPULATION = 'SP.POP.TOTL'
    AREA = 'AG.SRF.TOTL.K2'

    # данные по стране
    country_population = fetch_data_from_world_bank(country_code, POPULATION, year)
    country_area = fetch_data_from_world_bank(country_code, AREA, year)

    # данные по миру (код "WLD")
    world_population = fetch_data_from_world_bank("WLD", POPULATION, year)
    world_area = fetch_data_from_world_bank("WLD", AREA, year)

    # если каких-то данных нет, заменяем их на 0
    country_population = country_population if country_population else 0
    country_area = country_area if country_area else 0
    world_population = world_population if world_population else 1  # Избегаем деления на 0
    world_area = world_area if world_area else 1  # Избегаем деления на 0


    critical_mass = (country_population / world_population) * 100 + (country_area / world_area) * 100
    return round(critical_mass, 2)

# функция для расчета показателей
def calculate_metrics(selected_country):
    code = country_codes.get(selected_country)

    results = {}

    # ВВП
    gdp_data = fetch_data_from_world_bank(code, "NY.GDP.MKTP.CD") if code else None
    results["ВВП"] = gdp_data if gdp_data else 0  # Заменяем "Неизвестно" на 0

    # военные расходы
    military_spending, error_message = fetch_military_spending(military_spending_file, "Current US$", selected_country)
    results["Военные расходы"] = military_spending if military_spending else 0  # Заменяем "Неизвестно" на 0

    # экономическая силв
    world_gdp_data = fetch_data_from_world_bank("WLD", "NY.GDP.MKTP.CD")
    if gdp_data and world_gdp_data:
        economic_strength = (gdp_data / world_gdp_data) * 200
        results["Экономическая сила"] = round(economic_strength, 2)
    else:
        results["Экономическая сила"] = 0

    # военная сила
    if military_spending > 0:
        military_strength = (military_spending / militarySpending_total) * 200
        results["Военная сила"] = round(military_strength, 2)
    else:
        results["Военная сила"] = 0

    # критическая масса
    critical_mass = get_critical_mass(code)
    results["Критическая масса"] = critical_mass if critical_mass else 0

    # совокупная мощь чин-лунг
    power = (results["Критическая масса"] + results["Экономическая сила"] + results["Военная сила"]) / 3
    results["Совокупная мощь"] = round(power, 2)

    return results, error_message


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.title("Оценка совокупной мощи государств")
        self.geometry("1000x600")

        # Список добавленных стран
        self.added_countries = []

        # Главный экран
        self.show_main_screen()

    def show_main_screen(self):
        # очистка текущего содержимого
        for widget in self.winfo_children():
            widget.destroy()

        # фрейм для группы элементов выбора страны
        selection_frame = ctk.CTkFrame(self)
        selection_frame.pack(pady=20, padx=20, fill="x")

        self.country_label = ctk.CTkLabel(selection_frame, text="Выберите страну для расчета:")
        self.country_label.pack(side="left", padx=(0, 10))

        # выпадающий список стран
        self.country_combobox = ctk.CTkComboBox(
            selection_frame,
            values=list(country_codes.keys()),
            state="readonly",
            width=400
        )
        self.country_combobox.pack(side="left")

        self.add_button = ctk.CTkButton(self, text="Добавить страну", command=self.add_country)
        self.add_button.pack(padx = 20, anchor="w")

        # фрейм для таблицы
        self.scrollable_frame = ctk.CTkScrollableFrame(self, width=900, height=400)
        self.scrollable_frame.pack(padx=20, pady=20, fill="both", expand=True)
        headers = ["Страна", "ВВП в млн$", "Экономическая сила", "Военная сила", "Критическая масса", "Совокупная мощь"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.scrollable_frame, text=header, font=("Arial", 12, "bold"), anchor="w")
            label.grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # уведомления
        self.notification_label = ctk.CTkLabel(self, text="", font=("Arial", 12), anchor="ne", fg_color="orange", corner_radius=5)
        self.notification_label.place(relx=1, rely=0.035, anchor="ne")

    def add_country(self):
        selected_country = self.country_combobox.get()
        if not selected_country:
            print("Страна не выбрана!")
            return

        # проверка, была ли страна уже добавлена
        if selected_country in self.added_countries:
            print(f"Страна '{selected_country}' уже добавлена!")
            return

        # расчет показателей
        metrics, error_message = calculate_metrics(selected_country)
        self.added_countries.append(selected_country)

        # формат ВВП
        formatted_gdp = "{:,}".format(int(metrics["ВВП"])) if metrics["ВВП"] else "0"

        # заполнение таблицы данными
        row_data = [
            selected_country,
            formatted_gdp,
            str(metrics["Экономическая сила"]),
            str(metrics["Военная сила"]),
            str(metrics["Критическая масса"]),
            str(metrics["Совокупная мощь"])
        ]

        row = len(self.added_countries)

        for col, value in enumerate(row_data):
            fg_color = "#ADD8E6" if col == 5 else None
            value_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=value,
                anchor="w",
                fg_color=fg_color,
                corner_radius=5
            )
            value_label.grid(row=row, column=col, padx=10, pady=5, sticky="w")

        if error_message:
            self.show_notification(error_message)

    def show_notification(self, message):
        self.notification_label.configure(text=message)
        self.after(3000, lambda: self.notification_label.configure(text=""))



if __name__ == "__main__":
    app = App()
    app.mainloop()