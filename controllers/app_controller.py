class AppController:
    def __init__(self, model, view, formula_evaluator, exporter):
        self.model = model
        self.view = view
        self.evaluator = formula_evaluator
        self.exporter = exporter

        self.user_models = {}
        self.country_data = []

    def add_country(self, country_name):
        if not country_name:
            self.view.notify("Страна не выбрана!")
            return

        if country_name in [entry["Страна"] for entry in self.country_data]:
            self.view.notify(f"Страна '{country_name}' уже добавлена!")
            return

        metrics, error = self.model.calculate_metrics(country_name)
        if error:
            self.view.notify(error)

        row = {
            "Страна": country_name,
            "ВВП (млн USD)": metrics["ВВП"],
            "Военные расходы (млн USD)": metrics["Военные расходы"],
            "Совокупная мощь по Чин-Лунгу": metrics["Совокупная мощь по Чин-Лунгу"],
            "Индекс национального потенциала": metrics["Индекс национального потенциала"]
        }

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


        for widget in self.view.scrollable_frame.winfo_children():
            info = widget.grid_info()
            if int(info["row"]) > 0:
                widget.destroy()

        for row in self.country_data:
            base_metrics, _ = self.model.calculate_metrics(row["Страна"])
            row[name] = self.evaluator.evaluate(formula, base_metrics)
            self.view.add_table_row(row)

    def export_data(self):
        if not self.country_data:
            self.view.notify("Нет данных для экспорта!")
            return
        self.exporter.export(self.country_data)
        self.view.notify("Экспорт завершён!")

    def get_user_models(self):
        return self.user_models
