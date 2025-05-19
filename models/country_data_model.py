from dict import country_codes


class CountryDataModel:
    def __init__(self, db_connection_factory, parser, calculator):
        self.db_connection_factory = db_connection_factory
        self.parser = parser
        self.calculator = calculator

    def calculate_metrics(self, country_name, year):
        code = country_codes.get(country_name)
        conn = self.db_connection_factory()
        cursor = conn.cursor(dictionary=True)

        # 1. Попробовать найти в БД
        cursor.execute("SELECT * FROM country_metrics_full WHERE country_name = %s AND year = %s", (country_name, year))
        row = cursor.fetchone()
        if row:
            conn.close()
            return self._convert_row_to_metrics(row), None

        # 2. Если нет — рассчитать
        metrics, error_message = self.calculator.calculate(code, country_name, year)

        # 3. Сохранить в БД
        cursor.execute("""
            INSERT INTO country_metrics_full (
                country_name, year, gdp, military_spending, economic_strength, military_strength, critical_mass,
                power_chin_lung, gdp_ppp, gdp_ppp_per_capita, population, global_gdp,
                global_military_spending, global_gdp_ppp_per_capita, global_population,
                military_part, gdp_part, gdp_ppp_part, population_part, national_potential_index
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
