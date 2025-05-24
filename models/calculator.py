# класс для расчёта всех показателей на основе полученных данных
class Calculator:
    def __init__(self, parser):
        self.parser = parser
        self.military_spending_total = 2443398.80320217 * 1_000_000  # общий военный бюджет мира (можно заменить на расчёт по году)

    # функция расчёта критической массы страны (на основе населения и территории)
    def get_critical_mass(self, country_code, year=2023):
        POPULATION = 'SP.POP.TOTL'
        AREA = 'AG.SRF.TOTL.K2'

        pop = self.parser.fetch_data_from_world_bank(country_code, POPULATION, year) or 0
        area = self.parser.fetch_data_from_world_bank(country_code, AREA, year) or 0
        world_pop = self.parser.fetch_data_from_world_bank("WLD", POPULATION, year) or 1
        world_area = self.parser.fetch_data_from_world_bank("WLD", AREA, year) or 1

        return round((pop / world_pop) * 100 + (area / world_area) * 100, 2)

    # основная функция расчёта всех показателей мощности по стране и году
    def calculate(self, code, country_name, year):
        error_message = None

        # ВВП в миллионах долларов
        gdp_current = self.parser.fetch_data_from_world_bank(code, "NY.GDP.MKTP.CD", year) or 0
        gdp = round(gdp_current / 1_000_000, 2)

        # военные расходы по Excel
        military_spending, error_message = self.parser.fetch_military_spending(country_name, year)

        # экономическая сила (доля ВВП страны в мировом)
        world_gdp = self.parser.fetch_data_from_world_bank("WLD", "NY.GDP.MKTP.CD", year) or 1
        economic_strength = round((gdp_current / world_gdp) * 200, 2)

        # военная сила (доля военных расходов страны)
        military_strength = round((military_spending * 1_000_000 / self.military_spending_total) * 200, 2) if military_spending else 0

        # критическая масса
        critical_mass = self.get_critical_mass(code, year)

        # итоговая мощь по Чин-Лунгу
        power_chin_lung = round((critical_mass + economic_strength + military_strength) / 3, 2)

        # дополнительные показатели для индекса
        gdp_ppp = self.parser.fetch_data_from_world_bank(code, "NY.GDP.MKTP.PP.CD", year) or 0
        gdp_ppp_per_capita = self.parser.fetch_data_from_world_bank(code, "NY.GDP.PCAP.PP.CD", year) or 0
        population = self.parser.fetch_data_from_world_bank(code, "SP.POP.TOTL", year) or 0
        area = self.parser.fetch_data_from_world_bank(code, "AG.SRF.TOTL.K2", year) or 0  # площадь

        # мировые показатели
        global_gdp_ppp_per_capita = self.parser.fetch_data_from_world_bank("WLD", "NY.GDP.PCAP.PP.CD", year) or 1
        global_population = self.parser.fetch_data_from_world_bank("WLD", "SP.POP.TOTL", year) or 1

        # компоненты формулы индекса
        military_part = (military_spending * 1_000_000 / self.military_spending_total) * 0.29
        gdp_part = ((gdp_current * gdp_ppp_per_capita) / (world_gdp * global_gdp_ppp_per_capita)) * 0.1
        gdp_ppp_part = (gdp_ppp / world_gdp) * 0.35
        population_part = (population / global_population) * 0.26

        # рассчитанный индекс национального потенциала
        national_potential_index = round(military_part + gdp_part + gdp_ppp_part + population_part, 4)

        # словарь с показателями и сообщение об ошибке
        return {
            "ВВП": gdp,
            "Военные расходы": military_spending,
            "Экономическая сила": economic_strength,
            "Военная сила": military_strength,
            "Критическая масса": critical_mass,
            "Совокупная мощь по Чин-Лунгу": power_chin_lung,
            "ВВП ППС": gdp_ppp,
            "ВВП ППС на душу": gdp_ppp_per_capita,
            "Население": population,
            "Площадь": area,
            "Глобальный ВВП": world_gdp,
            "Глобальные военные расходы": self.military_spending_total,
            "Глобальный ВВП ППС на душу": global_gdp_ppp_per_capita,
            "Глобальное население": global_population,
            "Часть ВР": military_part,
            "Часть ВВП": gdp_part,
            "Часть ВВП ППС": gdp_ppp_part,
            "Часть населения": population_part,
            "Индекс национального потенциала": national_potential_index
        }, error_message
