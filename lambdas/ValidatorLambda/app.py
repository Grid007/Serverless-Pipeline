import json
import requests

def lambda_handler(event, context):
    try:
        # Fetch data from randomuser.me API
        response = requests.get("https://randomuser.me/api/")
        user_data = response.json()["results"][0]

        # Extract required fields
        name = f"{user_data['name']['first']} {user_data['name']['last']}"
        country = user_data['location']['country']
        uuid = user_data['login']['uuid']
        age = user_data['dob']['age']

        # Validate fields
        if not all([name, country, uuid, age]):
            raise ValueError("Missing required fields: name, country, uuid, age")

        # Return the payload for the next step
        return {
            "statusCode": 200,
            "body": json.dumps({
                "name": name,
                "country": country,
                "uuid": uuid,
                "age": age
            })
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "error": str(e)
            })
        }
