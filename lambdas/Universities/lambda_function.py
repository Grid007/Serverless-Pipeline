import json
import psycopg2
import psycopg2.extras
import os

# Database configuration
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']

def lambda_handler(event, context):
    try:
        country = event['country']
        universities = event['universities']

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        # Upsert university data into the 'universities' table
        insert_query = """
            INSERT INTO universities (name, country)
            VALUES (%s, %s)
            ON CONFLICT (name, country) DO NOTHING
        """
        records = [(uni['name'], country) for uni in universities]
        psycopg2.extras.execute_batch(cur, insert_query, records)
        conn.commit()

        cur.close()
        conn.close()

        # Return proper output structure and trigger the Fargate task
        return {
            "statusCode": 200,
            "message": f"Loaded {len(universities)} universities for {country}.",
            "country": country  # Pass the country to trigger Fargate task
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e)
        }
