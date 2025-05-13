import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def create_table():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
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
        """)

        connection.commit()
        print("Таблица country_metrics_full успешно создана.")

    except mysql.connector.Error as err:
        print(f"Ошибка: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_table()
