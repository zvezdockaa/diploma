import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",         # <-- замени
        password="your_password",     # <-- замени
        database="your_database"      # <-- замени
    )
