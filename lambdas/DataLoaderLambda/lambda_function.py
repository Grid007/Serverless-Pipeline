import json
import psycopg2
import os
import requests

# Database configuration
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']

def lambda_handler(event, context):
    try:
        # Extract payload
        payload = json.loads(event['body']) if 'body' in event else event
        name = payload['name']
        country = payload['country']
        uuid = payload['uuid']
        age = payload['age']

        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        cur = conn.cursor()

        # Upsert user data
        cur.execute("""
            INSERT INTO users (uuid, name, country, age)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (uuid) DO UPDATE
            SET name = EXCLUDED.name, country = EXCLUDED.country, age = EXCLUDED.age
        """, (uuid, name, country, age))
        conn.commit()

        # Check for university data
        cur.execute("SELECT COUNT(*) FROM universities WHERE country = %s", (country,))
        university_count = cur.fetchone()[0]

        cur.close()
        conn.close()

        if university_count == 0:
            # No university data found, fetch from API
            api_response = requests.get(f"http://universities.hipolabs.com/search?country={country}").json()
            if not api_response:
                return {
                    "statusCode": 500,
                    "error": "No universities found for country: {country}",
                    "action": "failure"
                }

            # Return to trigger LoadUniversitiesLambda
            return {
                "statusCode": 200,
                "action": "load_universities",
                "country": country,
                "universities": api_response
            }

        # University data exists, trigger Fargate task
        return {
            "statusCode": 200,
            "action": "trigger_fargate",
            "country": country
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "error": str(e),
            "action": "failure"
        }
