import mysql.connector

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='support_desk')
    return connection

