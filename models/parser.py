import requests
import openpyxl


class Parser:
    def __init__(self, military_spending_file="военные расходы.xlsx", sheet_name="Current US$"):
        self.military_spending_file = military_spending_file
        self.sheet_name = sheet_name

    def fetch_data_from_world_bank(self, country_code, indicator, year=2023):
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
            print(f"[Parser] Ошибка при получении данных: {e}")
            return None

    def fetch_military_spending(self, country_name):
        try:
            workbook = openpyxl.load_workbook(self.military_spending_file)
            sheet = workbook[self.sheet_name]
            for row in sheet.iter_rows(values_only=True):
                if str(row[0]).strip().lower() == country_name.strip().lower():
                    spending_str = str(row[1]).strip()
                    if spending_str.lower() in ["...", "nan", ""]:
                        return 0, f"Данные о военных расходах для страны '{country_name}' неизвестны"
                    try:
                        spending = float(spending_str.replace(",", ""))
                        return round(spending, 5), None
                    except ValueError:
                        return 0, f"Ошибка преобразования данных для страны '{country_name}'"
            return 0, f"Данные о военных расходах для страны '{country_name}' неизвестны"
        except Exception as e:
            raise ValueError(f"[Parser] Не удалось открыть файл: {e}")
