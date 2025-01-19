from fastapi import FastAPI, HTTPException
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from typing import List
import os

# Initialize FastAPI
app = FastAPI()

# ✅ Database Connection Function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",   # Change to your MySQL host (use Public IP if running remotely)
            user="root",      # Replace with your MySQL username
            password="teamx@123T",  # Replace with your MySQL password
            database="backtrack_db",
            port=3306
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print("Error while connecting to MySQL", e)
        return None

# ✅ Pydantic Model for Data
class BacktrackItem(BaseModel):
    category_name: str
    source_provider: str
    date: str
    time: str
    text_head: str
    detailed_text: str
    amount: float

# ✅ 1️⃣ Check Database Connection
@app.get("/")
def check_db():
    conn = get_db_connection()
    if conn:
        return {"message": "Connected to MySQL Database!"}
    else:
        raise HTTPException(status_code=500, detail="Database connection failed!")

# ✅ 2️⃣ Fetch all records
@app.get("/api/backtrack", response_model=List[BacktrackItem])
def get_all_records():
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed!")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM backtrack_table")
    rows = cursor.fetchall()
    conn.close()
    return rows

# ✅ 3️⃣ Insert a new record
@app.post("/api/backtrack")
def create_record(item: BacktrackItem):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed!")

    cursor = conn.cursor()
    sql = """INSERT INTO backtrack_table (category_name, source_provider, date, time, text_head, detailed_text, amount)
             VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    values = (item.category_name, item.source_provider, item.date, item.time, item.text_head, item.detailed_text, item.amount)
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return {"message": "Record added successfully"}

# ✅ 4️⃣ Fetch a single record by ID
@app.get("/api/backtrack/{record_id}")
def get_record(record_id: int):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed!")

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM backtrack_table WHERE id = %s", (record_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Record not found")
    return row
