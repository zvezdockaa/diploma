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

            # Найдём первое непустое значение
            for entry in data[1]:
                value = entry.get("value")
                if value is not None:
                    return value
            return None

        except requests.exceptions.RequestException as e:
            print(f"[Parser] Ошибка при получении данных с World Bank API: {e}")
            return None

    def fetch_military_spending(self, country_name, year=2023):
        try:
            workbook = openpyxl.load_workbook(self.military_spending_file, data_only=True)
            sheet = workbook[self.sheet_name]

            # Найдём индекс столбца нужного года
            year_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))
            year_col_index = None
            for idx, cell in enumerate(year_row):
                if str(cell).strip() == str(year):
                    year_col_index = idx
                    break

            if year_col_index is None:
                return 0, f"Год {year} не найден в файле военных расходов."

            # Найдём нужную страну и извлечём значение
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if str(row[0]).strip().lower() == country_name.strip().lower():
                    spending_str = str(row[year_col_index]).strip()
                    if spending_str.lower() in ["...", "nan", ""]:
                        return 0, f"Данные о военных расходах для страны '{country_name}' за {year} неизвестны"
                    try:
                        spending = float(spending_str.replace(",", ""))
                        return round(spending, 5), None
                    except ValueError:
                        return 0, f"Ошибка преобразования данных для '{country_name}' за {year}"
            return 0, f"Страна '{country_name}' не найдена в таблице военных расходов"

        except Exception as e:
            raise ValueError(f"[Parser] Не удалось открыть или прочитать файл: {e}")

