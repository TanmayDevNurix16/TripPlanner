import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="teamx@123T",
    database="backtrack_db"
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM backtrack_table")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
