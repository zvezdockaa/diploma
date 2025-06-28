class AppController:
    def __init__(self, model, view, formula_evaluator, exporter):
        self.model = model
        self.view = view
        self.evaluator = formula_evaluator
        self.exporter = exporter

        self.user_models = {}
        self.country_data = []  # список строк с данными

    def add_country(self, country_name, year):
        if not country_name:
            self.view.notify("Страна не выбрана!")
            return

        # защита от дубликатов
        if any(row["Страна"] == country_name and row["Год"] == year for row in self.country_data):
            self.view.notify(f"Страна '{country_name}' за {year} уже добавлена!")
            return

        metrics, error = self.model.calculate_metrics(country_name, year)
        if error:
            self.view.notify(error)
        if not metrics.get("ВВП") or metrics["ВВП"] == 0:
            self.view.notify(f"Нет данных о ВВП для '{country_name}' за {year}")


        # базовая строка
        row = {
            "Страна": country_name,
            "Год": year,
            "ВВП (млн USD)": metrics["ВВП"],
            "Военные расходы (млн USD)": metrics["Военные расходы"],
            "Совокупная мощь по Чин Лунгу": metrics["Совокупная мощь по Чин Лунгу"],
            "Индекс национального потенциала": metrics["Индекс национального потенциала"]
        }

        # применяем все пользовательские формулы
        for name, formula in self.user_models.items():
            row[name] = self.evaluator.evaluate(formula, metrics)

        self.country_data.append(row)
        self.view.add_table_row(row)

    def add_user_model(self, name, formula):
        if name in self.user_models:
            self.view.notify(f"Модель '{name}' уже существует!")
            return

        self.user_models[name] = formula
        self.view.user_models.append(name)
        self.view.build_table_headers()

        # обновляем значения для всех строк
        for i, row in enumerate(self.country_data):
            base_metrics, _ = self.model.calculate_metrics(row["Страна"], row["Год"])
            row[name] = self.evaluator.evaluate(formula, base_metrics)

        # перерисовываем таблицу
        for widget in self.view.scrollable_frame.winfo_children():
            if int(widget.grid_info().get("row", 0)) > 0:
                widget.destroy()

        for row in self.country_data:
            self.view.add_table_row(row)

    def export_data(self):
        if not self.country_data:
            self.view.notify("Нет данных для экспорта!")
            return
        self.exporter.export(self.country_data)
        self.view.notify("Экспорт завершён!")

    def get_added_country_names(self) -> list:
        return list({row["Страна"] for row in self.country_data})

    def get_available_indicators(self) -> list:
        return [key for key in self.country_data[0].keys() if key not in ("Страна", "Год")] if self.country_data else []

    def get_country_data_by_year(self, country: str, indicator: str) -> dict:
        result = {}
        for row in self.country_data:
            if row["Страна"] == country and indicator in row:
                try:
                    result[int(row["Год"])] = float(row[indicator])
                except (ValueError, TypeError):
                    continue
        return result

    def get_indicator_across_countries(self, indicator: str) -> dict:
        result = {}
        for row in self.country_data:
            try:
                result[row["Страна"]] = float(row[indicator])
            except (ValueError, TypeError, KeyError):
                continue
        return result

    def save_user_model_to_db(self, name, formula):
        conn = self.model.db_connection_factory()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO UserModels (name, formula)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE formula = VALUES(formula)
        """, (name, formula))
        conn.commit()
        conn.close()
        self.view.notify(f"Модель '{name}' сохранена в базу данных.")

    def has_user_models(self) -> bool:
        conn = self.model.db_connection_factory()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM UserModels")
        result = cursor.fetchone()
        conn.close()
        return result["count"] > 0 if result else False

    def load_user_models(self):
        conn = self.model.db_connection_factory()
        cursor = conn.cursor()
        cursor.execute("SELECT ModelName, FormulaText FROM UserModels")
        models = cursor.fetchall()
        conn.close()

        for model in models:
            self.add_user_model(model["ModelName"], model["FormulaText"])

    def get_user_model_names(self):
        conn = self.model.db_connection_factory()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM UserModels")
        names = [row["name"] for row in cursor.fetchall()]
        conn.close()
        return names

    def load_selected_user_models(self, model_names):
        if not model_names:
            return

        conn = self.model.db_connection_factory()
        cursor = conn.cursor()
        format_strings = ','.join(['%s'] * len(model_names))
        cursor.execute(f"SELECT name, formula FROM UserModels WHERE name IN ({format_strings})", tuple(model_names))
        models = cursor.fetchall()
        conn.close()

        for model in models:
            self.add_user_model(model["name"], model["formula"])

