import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='vacante'
        )
        if connection.is_connected():
            return connection
        else:
            return None
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None
