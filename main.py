# from fastapi import FastAPI, HTTPException,Query
# import mysql.connector
# from mysql.connector import Error
# from pydantic import BaseModel
# from typing import List,Dict
# from datetime import datetime, timedelta
# import os
# from fastapi.middleware.cors import CORSMiddleware
# # Initialize FastAPI
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Frontend URL (e.g., Vite dev server URL)
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all HTTP methods
#     allow_headers=["*"],  # Allows all headers
# )
# # ✅ Database Connection Function
# def get_db_connection():
#     try:
#         conn = mysql.connector.connect(
#             host="localhost",   # Change to your MySQL host (use Public IP if running remotely)
#             user="root",      # Replace with your MySQL username
#             password="teamx@123T",  # Replace with your MySQL password
#             database="backtrack_db",
#             port=3306
#         )
#         if conn.is_connected():
#             return conn
#     except Error as e:
#         print("Error while connecting to MySQL", e)
#         return None

# # ✅ Pydantic Model for Data
# class BacktrackItem(BaseModel):
#     category_name: str

#     source_provider: str
#     date: str
#     time: str
#     text_head: str
#     detailed_text: str
#     amount: float

# # ✅ 1️⃣ Check Database Connection
# @app.get("/")
# def check_db():
#     conn = get_db_connection()
#     if conn:
#         return {"message": "Connected to MySQL Database!"}
#     else:
#         raise HTTPException(status_code=500, detail="Database connection failed!")

# # ✅ 2️⃣ Fetch all records
# @app.get("/api/backtrack", response_model=List[BacktrackItem])
# def get_all_records():
#     conn = get_db_connection()
#     if conn is None:
#         raise HTTPException(status_code=500, detail="Database connection failed!")
    
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM backtrack_table")
#     rows = cursor.fetchall()
#     conn.close()
#     return rows



# # ✅ 4️⃣ Fetch a single record by ID
# @app.get("/api/backtrack/{record_id}")
# def get_record(record_id: int):
#     conn = get_db_connection()
#     if conn is None:
#         raise HTTPException(status_code=500, detail="Database connection failed!")

#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM backtrack_table WHERE id = %s", (record_id,))
#     row = cursor.fetchone()
#     conn.close()
#     if not row:
#         raise HTTPException(status_code=404, detail="Record not found")
#     return row

from fastapi import FastAPI, HTTPException, Query
import mysql.connector
from mysql.connector import Error
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL (e.g., Vite dev server URL)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# ✅ Database Connection Function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",   
            user="root",        
            password="teamx@123T",  
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

# ✅ 5️⃣ Fetch total expenditure per category within a given period
@app.get("/category_percent_data")
def get_category_percent_data(
    period: int = Query(..., ge=1, le=30, description="Number of days between 1 and 30"),
    date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Retrieve total expenditure per category for the given period (1-30 days) ending at 'date'.
    Only includes the categories:
    - food_spending
    - health_and_fitness
    - home_and_living
    - music_and_entertainment
    - savings_and_investments
    """
    try:
        # Convert date string to datetime object
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=period)

        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed!")

        cursor = conn.cursor(dictionary=True)

        # ✅ SQL Query: Get total expenditure for the 5 categories only
        sql_query = """
        SELECT category_name, SUM(amount) AS total_expenditure
        FROM backtrack_table
        WHERE date BETWEEN %s AND %s
        AND category_name IN ('food_spending', 'health_and_fitness', 'home_and_living', 
                              'music_and_entertainment', 'savings_and_investments')
        GROUP BY category_name
        ORDER BY total_expenditure DESC;
        """
        
        cursor.execute(sql_query, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        category_data = cursor.fetchall()

        # Compute total spending across selected categories
        total_spending = sum(item["total_expenditure"] for item in category_data)

        # Calculate percentage for each category, rounded to whole number
        for item in category_data:
            item["percentage"] = round((item["total_expenditure"] / total_spending) * 100) if total_spending > 0 else 0

        conn.close()

        return {"total_spending": total_spending, "category_data": category_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/overall_data_desc")
def get_overall_expenditure_desc(
    period: int = Query(..., ge=1, le=30, description="Number of days between 1 and 30"),
    date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Returns a dictionary where each category contains a list of [date, expenditure] 
    pairs sorted in increasing order of date.
    """
    try:
        # Convert date string to datetime object
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=period)

        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed!")

        cursor = conn.cursor(dictionary=True)

        # SQL Query to retrieve expenditure data ordered by date
        sql_query = """
        SELECT category_name, date, SUM(amount) AS total_expenditure
        FROM backtrack_table
        WHERE date BETWEEN %s AND %s
        GROUP BY category_name, date
        ORDER BY date DESC;
        """
        
        cursor.execute(sql_query, (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        expenditure_data = cursor.fetchall()
        conn.close()

        # Organizing data into dictionary
        result = {}
        for row in expenditure_data:
            category = row["category_name"]
            date = row["date"]
            expenditure = row["total_expenditure"]

            if category not in result:
                result[category] = []
            result[category].append([date, expenditure])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/overall")
def get_overall_expenditure():
    """
    Returns a dictionary where each category contains a list of [date, expenditure] 
    pairs sorted in increasing order of date.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed!")

        cursor = conn.cursor(dictionary=True)

        # SQL Query to retrieve expenditure data ordered by date
        sql_query = """
        SELECT category_name, date, SUM(amount) AS total_expenditure
        FROM backtrack_table
        GROUP BY category_name, date
        ORDER BY date ASC;
        """
        
        cursor.execute(sql_query)
        expenditure_data = cursor.fetchall()
        conn.close()

        # Organizing data into dictionary
        result = {}
        for row in expenditure_data:
            category = row["category_name"]
            date = row["date"]
            expenditure = row["total_expenditure"]

            if category not in result:
                result[category] = []
            result[category].append([date, expenditure])

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ 2️⃣ Get Expenditure Trend for a Specific Source Provider

    
@app.get("/api/set_level")
def set_level(l: int = Query(..., description="Set level (0, 1, or 2)", ge=0, le=2)):
    """
    Updates the 'level' value in 'level_table' with the provided value (0, 1, or 2).
    """
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed!")

        cursor = conn.cursor()

        # Update or insert level value
        sql_query = """
        INSERT INTO level_table (id, level) 
        VALUES (1, %s) 
        ON DUPLICATE KEY UPDATE level = %s;
        """
        cursor.execute(sql_query, (l, l))
        conn.commit()
        conn.close()

        return {"message": f"Level set to {l}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ 2️⃣ Get Level: /api/get_level
@app.get("/api/get_level")
def get_level():
    """
    Retrieves the current 'level' value stored in 'level_table'.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed!")

        cursor = conn.cursor(dictionary=True)

        # ✅ Force MySQL to get the latest data
        conn.commit()  # Ensures any previous uncommitted changes are flushed

        # Fetch level value
        sql_query = "SELECT level FROM level_table WHERE id = 1;"
        cursor.execute(sql_query)
        level_data = cursor.fetchone()
        conn.close()

        if level_data is None:
            raise HTTPException(status_code=404, detail="No level data found")

        return level_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/food")
def get_food_spending():
    """
    Retrieves the total expenditure for Zomato, Swiggy, Zepto, Dominos, and EatFit
    in the food_spending category from 15 Dec 2024 to 15 Jan 2025.
    Also calculates each provider's percentage of the total food spending.
    """
    try:
        # Define date range
        start_date = "2024-12-15"
        end_date = "2025-01-15"

        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed!")

        cursor = conn.cursor(dictionary=True)

        # ✅ SQL Query: Get total expenditure per provider within the date range
        sql_query = """
        SELECT source_provider, SUM(amount) AS total_expenditure
        FROM backtrack_table
        WHERE category_name = 'food_spending'
        AND source_provider IN ('Zomato', 'Swiggy', 'Zepto', 'Dominos', 'EatFit')
        AND date BETWEEN %s AND %s
        GROUP BY source_provider
        ORDER BY total_expenditure DESC;
        """
        
        cursor.execute(sql_query, (start_date, end_date))
        provider_data = cursor.fetchall()

        # Compute total spending across all 5 providers
        total_spending = sum(item["total_expenditure"] for item in provider_data)

        # Calculate percentage for each provider, rounded to whole numbers
        for item in provider_data:
            item["percentage"] = round((item["total_expenditure"] / total_spending) * 100) if total_spending > 0 else 0

        conn.close()

        return {"total_spending": total_spending, "food_providers": provider_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/insights/overall")
def get_zomato_weekly_insights():
        return {
            "POSITIVE": "You saved INR 15746 in home_and_living expenses last week(05-01-2025 to 11-01-2025) compared to week before (29-12-2024 to 04-01-2025)",
            "NEGATIVE": "You overspent INR 34086 in food_spending last week(05-01-2025 to 11-01-2025) compared to week before (29-12-2024 to 04-01-2025)",
            "SUGGESTION": "Kudos! Your overall spend reduced by INR 11326. Try to save more on food and entertainment."
        }

    
@app.get("/desc/{category_name}")
def get_category_expenditure_by_source(
    category_name: str,
    period: int = Query(..., ge=1, le=30, description="Number of days between 1 and 30"),
    date: str = Query(..., description="End date in YYYY-MM-DD format")
):
    """
    Retrieves total expenditure for a given category, grouped by source provider, 
    sorted by date (descending).
    """
    try:
        # Convert date string to datetime object
        end_date = datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=period)

        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed!")

        cursor = conn.cursor(dictionary=True)

        # ✅ SQL Query: Retrieve category-wise expenditure grouped by source_provider
        sql_query = """
        SELECT source_provider, date, SUM(amount) AS total_expenditure
        FROM backtrack_table
        WHERE category_name = %s
        AND date BETWEEN %s AND %s
        GROUP BY source_provider, date
        ORDER BY date DESC;
        """
        
        cursor.execute(sql_query, (category_name, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        expenditure_data = cursor.fetchall()
        conn.close()

        # Organizing data into dictionary by source_provider
        result = {}
        for row in expenditure_data:
            provider = row["source_provider"]
            date = row["date"]
            expenditure = row["total_expenditure"]

            if provider not in result:
                result[provider] = []
            result[provider].append([date, expenditure])

        if not result:
            raise HTTPException(status_code=404, detail=f"No expenditure data found for category: {category_name}")

        return {"category": category_name, "source_providers": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))