from dict import country_codes

# модель для получения и сохранения расчетных данных по стране
class CountryDataModel:
    def __init__(self, db_connection_factory, parser, calculator):
        self.db_connection_factory = db_connection_factory
        self.parser = parser
        self.calculator = calculator

        self.metrics = [
            "ВВП", "Военные расходы", "Экономическая сила", "Военная сила", "Критическая масса",
            "Совокупная мощь по Чин Лунгу", "ВВП ППС", "ВВП ППС на душу", "Население", "Площадь",
            "Глобальный ВВП", "Глобальные военные расходы", "Глобальный ВВП ППС на душу",
            "Глобальное население", "Часть ВР", "Часть ВВП", "Часть ВВП ППС", "Часть населения",
            "Индекс национального потенциала"
        ]

    def calculate_metrics(self, country_name, year):
        code = country_codes.get(country_name)
        conn = self.db_connection_factory()
        cursor = conn.cursor()

        # Получаем или вставляем страну, чтобы получить её ID
        cursor.execute("SELECT id FROM country WHERE code = %s", (code,))
        row = cursor.fetchone()

        if not row:
            cursor.execute("INSERT IGNORE INTO country (code, name) VALUES (%s, %s)", (code, country_name))
            conn.commit()
            cursor.execute("SELECT id FROM country WHERE code = %s", (code,))
            row = cursor.fetchone()

        country_id = row["id"]

        # Проверяем наличие рассчитанных данных
        cursor.execute("SELECT * FROM country_data WHERE country_id = %s AND year = %s", (country_id, year))
        row = cursor.fetchone()
        if row:
            cursor.execute("SELECT * FROM global_data WHERE year = %s", (year,))
            global_row = cursor.fetchone()
            conn.close()
            return self._merge_rows_to_metrics(row, global_row), None

        # данных нет - рассчитываем
        metrics, error_message = self.calculator.calculate(code, country_name, year)

        # сохраняем в таблицу country_data
        cursor.execute("""
            INSERT INTO country_data (
                country_id, year, gdp, gdp_ppp, gdp_ppp_per_capita, military_spending, population, area,
                economic_strength, military_strength, critical_mass,
                power_chin_lung, gdp_part, gdp_ppp_part, military_part,
                population_part, national_potential_index
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                gdp = VALUES(gdp),
                gdp_ppp = VALUES(gdp_ppp),
                gdp_ppp_per_capita = VALUES(gdp_ppp_per_capita),
                military_spending = VALUES(military_spending),
                population = VALUES(population),
                area = VALUES(area),
                economic_strength = VALUES(economic_strength),
                military_strength = VALUES(military_strength),
                critical_mass = VALUES(critical_mass),
                power_chin_lung = VALUES(power_chin_lung),
                gdp_part = VALUES(gdp_part),
                gdp_ppp_part = VALUES(gdp_ppp_part),
                military_part = VALUES(military_part),
                population_part = VALUES(population_part),
                national_potential_index = VALUES(national_potential_index)
        """, (
            country_id, year,
            metrics["ВВП"],
            metrics["ВВП ППС"],
            metrics["ВВП ППС на душу"],
            metrics["Военные расходы"],
            metrics["Население"],
            metrics["Площадь"],
            metrics["Экономическая сила"],
            metrics["Военная сила"],
            metrics["Критическая масса"],
            metrics["Совокупная мощь по Чин Лунгу"],
            metrics["Часть ВВП"],
            metrics["Часть ВВП ППС"],
            metrics["Часть ВР"],
            metrics["Часть населения"],
            metrics["Индекс национального потенциала"]
        ))

        # сохраняем в таблицу global_data
        cursor.execute("""
            INSERT INTO global_data (
                year, global_gdp, global_military_spending,
                global_gdp_ppp_per_capita, global_population, global_area
            ) VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                global_gdp = VALUES(global_gdp),
                global_military_spending = VALUES(global_military_spending),
                global_gdp_ppp_per_capita = VALUES(global_gdp_ppp_per_capita),
                global_population = VALUES(global_population),
                global_area = VALUES(global_area)
        """, (
            year,
            metrics["Глобальный ВВП"],
            metrics["Глобальные военные расходы"],
            metrics["Глобальный ВВП ППС на душу"],
            metrics["Глобальное население"],
            metrics["Площадь"]  # если хочешь — можно заменить на глобальную площадь
        ))

        conn.commit()
        conn.close()
        if error_message:
            metrics = {m: 0 for m in self.metrics}
        return metrics, error_message


    def _merge_rows_to_metrics(self, row, global_row):
        return {
            "Год": row["year"],
            "ВВП": row["gdp"],
            "Военные расходы": row["military_spending"],
            "Экономическая сила": row["economic_strength"],
            "Военная сила": row["military_strength"],
            "Критическая масса": row["critical_mass"],
            "Совокупная мощь по Чин Лунгу": row["power_chin_lung"],
            "ВВП ППС": row["gdp_ppp"],
            "ВВП ППС на душу": row["gdp_ppp_per_capita"],
            "Население": row["population"],
            "Площадь": row["area"],
            "Глобальный ВВП": global_row["global_gdp"] if global_row else None,
            "Глобальные военные расходы": global_row["global_military_spending"] if global_row else None,
            "Глобальный ВВП ППС на душу": global_row["global_gdp_ppp_per_capita"] if global_row else None,
            "Глобальное население": global_row["global_population"] if global_row else None,
            "Часть ВР": row["military_part"],
            "Часть ВВП": row["gdp_part"],
            "Часть ВВП ППС": row["gdp_ppp_part"],
            "Часть населения": row["population_part"],
            "Индекс национального потенциала": row["national_potential_index"]
        }
