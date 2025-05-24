from dict import country_codes

# модель для получения и сохранения расчетных данных по стране
class CountryDataModel:
    def __init__(self, db_connection_factory, parser, calculator):
        self.db_connection_factory = db_connection_factory
        self.parser = parser
        self.calculator = calculator

        # список показателей, которые участвуют в расчете и могут использоваться в формулах
        self.metrics = [
            "ВВП", "Военные расходы", "Экономическая сила", "Военная сила", "Критическая масса",
            "Совокупная мощь по Чин-Лунгу", "ВВП ППС", "ВВП ППС на душу", "Население", "Площадь",
            "Глобальный ВВП", "Глобальные военные расходы", "Глобальный ВВП ППС на душу",
            "Глобальное население", "Часть ВР", "Часть ВВП", "Часть ВВП ППС", "Часть населения",
            "Индекс национального потенциала"
        ]

    # функция возвращает словарь показателей по стране и году
    # если данные есть в БД — возвращает их, если нет — выполняет расчет и сохраняет результат
    def calculate_metrics(self, country_name, year):
        code = country_codes.get(country_name)
        conn = self.db_connection_factory()
        cursor = conn.cursor(dictionary=True)

        # попытка получить данные из базы
        cursor.execute("SELECT * FROM country_metrics_full WHERE country_name = %s AND year = %s", (country_name, year))
        row = cursor.fetchone()
        if row:
            conn.close()
            return self._convert_row_to_metrics(row), None

        # если данных нет — рассчитываем
        metrics, error_message = self.calculator.calculate(code, country_name, year)

        # сохраняем результат в базу
        cursor.execute("""
            INSERT INTO country_metrics_full (
                country_name, year, gdp, military_spending, economic_strength, military_strength, critical_mass,
                power_chin_lung, gdp_ppp, gdp_ppp_per_capita, population, area,
                global_gdp, global_military_spending, global_gdp_ppp_per_capita, global_population,
                military_part, gdp_part, gdp_ppp_part, population_part, national_potential_index
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            country_name,
            year,
            metrics["ВВП"],
            metrics["Военные расходы"],
            metrics["Экономическая сила"],
            metrics["Военная сила"],
            metrics["Критическая масса"],
            metrics["Совокупная мощь по Чин-Лунгу"],
            metrics["ВВП ППС"],
            metrics["ВВП ППС на душу"],
            metrics["Население"],
            metrics["Площадь"],
            metrics["Глобальный ВВП"],
            metrics["Глобальные военные расходы"],
            metrics["Глобальный ВВП ППС на душу"],
            metrics["Глобальное население"],
            metrics["Часть ВР"],
            metrics["Часть ВВП"],
            metrics["Часть ВВП ППС"],
            metrics["Часть населения"],
            metrics["Индекс национального потенциала"]
        ))

        conn.commit()
        conn.close()
        return metrics, error_message

    # функция преобразует строку из базы в словарь с метриками
    def _convert_row_to_metrics(self, row):
        return {
            "Год": row["year"],
            "ВВП": row["gdp"],
            "Военные расходы": row["military_spending"],
            "Экономическая сила": row["economic_strength"],
            "Военная сила": row["military_strength"],
            "Критическая масса": row["critical_mass"],
            "Совокупная мощь по Чин-Лунгу": row["power_chin_lung"],
            "ВВП ППС": row["gdp_ppp"],
            "ВВП ППС на душу": row["gdp_ppp_per_capita"],
            "Население": row["population"],
            "Площадь": row["area"],
            "Глобальный ВВП": row["global_gdp"],
            "Глобальные военные расходы": row["global_military_spending"],
            "Глобальный ВВП ППС на душу": row["global_gdp_ppp_per_capita"],
            "Глобальное население": row["global_population"],
            "Часть ВР": row["military_part"],
            "Часть ВВП": row["gdp_part"],
            "Часть ВВП ППС": row["gdp_ppp_part"],
            "Часть населения": row["population_part"],
            "Индекс национального потенциала": row["national_potential_index"]
        }
