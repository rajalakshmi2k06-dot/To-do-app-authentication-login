import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",          # உன்னோட MySQL username
    "password": "",  # உன்னோட MySQL password
    "database": "todo_app"
}

def get_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn