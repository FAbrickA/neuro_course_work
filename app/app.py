import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

DATABASE_URL = f"postgres://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

model = joblib.load("prediction_model.pkl")
vectorizer = joblib.load("count_vectorizer.pkl")


class User(BaseModel):
    username: str
    password: str


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# Создание таблицы пользователей
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()


def scan_for_sql_injection(text):
    """Return True if it is sql-injection"""

    new_queries_transformed = vectorizer.transform([text]).toarray()
    prediction = model.predict(new_queries_transformed)[0]
    return prediction == 1


create_table()


@app.post("/register/")
async def register_user(user: User):
    create_table()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Уязвимость: используется строка, составленная напрямую с данными пользователя
    # Возможна SQL-инъекция через user.username
    if scan_for_sql_injection(user.username):
        print(f"Замечена попытка использования sql-инъекции: {user.username}")
        raise HTTPException(status_code=400, detail=f"SQL-injection detected!")
    query = f"INSERT INTO users (username, password) VALUES ('{user.username}', '{user.password}');"
    try:
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()

    return {"message": f"User '{user.username}' registered successfully!"}
