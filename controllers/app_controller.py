# реализация класса Контроллер, связывает модели и предствление
class AppController:
    def __init__(self, model, view, formula_evaluator, exporter):
        self.model = model
        self.view = view
        self.evaluator = formula_evaluator
        self.exporter = exporter

        self.user_models = {}
        self.country_data = []
#функция добавления страны в таблицу для расчета
    def add_country(self, country_name, year):
        if not country_name:
            self.view.notify("Страна не выбрана!")
            return

        if any(entry["Страна"] == country_name and entry["Год"] == year for entry in self.country_data):
            self.view.notify(f"Страна '{country_name}' за {year} уже добавлена!")
            return

        metrics, error = self.model.calculate_metrics(country_name, year)
        if error:
            self.view.notify(error)

        if not metrics.get("ВВП") or metrics["ВВП"] == 0:
            self.view.notify(f"Нет данных о ВВП для '{country_name}' за {year}")

        row = {
            "Страна": country_name,
            "Год": year,
            "ВВП (млн USD)": metrics["ВВП"],
            "Военные расходы (млн USD)": metrics["Военные расходы"],
            "Совокупная мощь по Чин-Лунгу": metrics["Совокупная мощь по Чин-Лунгу"],
            "Индекс национального потенциала": metrics["Индекс национального потенциала"]
        }

        for name, formula in self.user_models.items():
            row[name] = self.evaluator.evaluate(formula, metrics)

        self.country_data.append(row)
        self.view.add_table_row(row)
#функция добавления пользовательской модели расчета
    def add_user_model(self, name, formula):
        if name in self.user_models:
            self.view.notify(f"Модель '{name}' уже существует!")
            return

        self.user_models[name] = formula
        self.view.user_models.append(name)
        self.view.build_table_headers()

        for widget in self.view.scrollable_frame.winfo_children():
            info = widget.grid_info()
            if int(info["row"]) > 0:
                widget.destroy()

        for row in self.country_data:
            base_metrics, _ = self.model.calculate_metrics(row["Страна"], row["Год"])
            row[name] = self.evaluator.evaluate(formula, base_metrics)
            self.view.add_table_row(row)

#функция экспорта данных расчета в файл excel
    def export_data(self):
        if not self.country_data:
            self.view.notify("Нет данных для экспорта!")
            return
        self.exporter.export(self.country_data)
        self.view.notify("Экспорт завершён!")

# функция возвращающая список добавленных стран
    def get_added_country_names(self) -> list:
        return list({row['Страна'] for row in self.country_data})

    # функция возвращающая список всех доступных показателей
    def get_available_indicators(self) -> list:
        if not self.country_data:
            return []

        indicators = set()
        for row in self.country_data:
            for key in row.keys():
                if key not in ['Страна', 'Год']:  # исключаем служебные поля
                    indicators.add(key)
        return list(indicators)

    # функция возвращающая значения конкретного показателя по годам для одной страны
    def get_country_data_by_year(self, country: str, indicator: str) -> dict:
        data_by_year = {}
        for row in self.country_data:
            if row['Страна'] == country and indicator in row:
                try:
                    year = int(row['Год'])
                    value = float(row[indicator])
                    data_by_year[year] = value
                except (ValueError, TypeError):
                    continue
        return data_by_year

    # функция возвращает значения показателя для всех стран (один показатель на страну)
    def get_indicator_across_countries(self, indicator: str) -> dict:
        country_values = {}
        for row in self.country_data:
            country = row['Страна']
            try:
                value = float(row.get(indicator, None))
                country_values[country] = value
            except (ValueError, TypeError):
                continue
        return country_values