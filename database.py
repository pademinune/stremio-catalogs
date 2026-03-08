
from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';")
cur.execute("SELECT * FROM users")

print(cur.fetchall())

# cur.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         id SERIAL PRIMARY KEY,
#         token VARCHAR(64) UNIQUE NOT NULL,
#         language VARCHAR(10) DEFAULT 'en',
#         genres JSONB DEFAULT '[]',
#         created_at TIMESTAMP DEFAULT NOW()
#     )
# """)

cur.execute("""
    INSERT INTO users (token, language, genres)
    VALUES (%s, %s, %s)
""", ("abatok3nag42", "en", '[3, 5]'))

conn.commit()

cur.close()
conn.close()

