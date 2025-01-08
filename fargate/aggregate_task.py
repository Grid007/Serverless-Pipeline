import os
import sys
import psycopg2

# Get country from command-line argument
country = sys.argv[1]  # Country passed from Step Function via ECS task command

# Check if country is provided
if not country:
    raise ValueError("Country argument is required.")

# Environment variables for DB connection
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASS")

# PostgreSQL connection
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
cursor = conn.cursor()

# Get number of universities in the specified country
cursor.execute("SELECT COUNT(*) FROM universities WHERE country = %s", (country,))
universities_count = cursor.fetchone()[0]

# Get number of users below 30 years in the specified country
cursor.execute("SELECT COUNT(*) FROM users WHERE country = %s AND age < 30", (country,))
users_under_30_count = cursor.fetchone()[0]


cursor.execute("INSERT INTO aggregate_data (country, universities_count, users_under_30_count) VALUES (%s, %s, %s)",
               (country, universities_count, users_under_30_count))

# Commit and close
conn.commit()
cursor.close()
conn.close()

print(f"Aggregation completed for country: {country}")
