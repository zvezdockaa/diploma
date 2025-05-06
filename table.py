import mysql.connector

def create_table():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_username",         # <-- замени
            password="your_password",     # <-- замени
            database="your_database"      # <-- замени
        )

        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS country_metrics_full (
            country_name VARCHAR(100) PRIMARY KEY,
            gdp FLOAT,
            military_spending FLOAT,
            economic_strength FLOAT,
            military_strength FLOAT,
            critical_mass FLOAT,
            power_chin_lung FLOAT,
            gdp_ppp FLOAT,
            gdp_ppp_per_capita FLOAT,
            population BIGINT,
            global_gdp FLOAT,
            global_military_spending FLOAT,
            global_gdp_ppp_per_capita FLOAT,
            global_population BIGINT,
            military_part FLOAT,
            gdp_part FLOAT,
            gdp_ppp_part FLOAT,
            population_part FLOAT,
            national_potential_index FLOAT
        );
        """

        cursor.execute(create_table_query)
        connection.commit()
        print("Таблица успешно создана.")
    except mysql.connector.Error as err:
        print(f"Ошибка: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_table()
