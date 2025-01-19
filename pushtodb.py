import mysql.connector
import os

# Database connection details
DB_CONFIG = {
    "host": "localhost",         # Change to your MySQL host if remote
    "user": "root",              # Change if using a different MySQL user
    "password": "teamx@123T",  # Change to your MySQL password
    "database": "backtrack_db",  # Change to your database name
    "port": 3306                 # Default MySQL port
}

# SQL file path
SQL_FILE_PATH = "food_data.sql"  # Change this path to your actual file location

# Function to connect to MySQL and execute queries
def execute_sql_file():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Read the SQL file
        with open(SQL_FILE_PATH, "r") as file:
            sql_queries = file.read()

        # Split queries to handle multiple statements
        queries = sql_queries.split(";")  # Splitting queries using ';'
        
        for query in queries:
            query = query.strip()  # Remove unnecessary spaces
            if query:  # Ensure query is not empty
                try:
                    cursor.execute(query)  # Execute each query
                    print(f"Executed: {query[:100]}...")  # Print part of the query executed
                except mysql.connector.Error as err:
                    print(f"Error executing query: {err}")

        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ All queries executed successfully!")

    except mysql.connector.Error as e:
        print(f"❌ Database connection failed: {e}")

# Run the function
execute_sql_file()
