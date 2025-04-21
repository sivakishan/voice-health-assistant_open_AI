import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def make_reservation_call(to_number, medicine_name):
    api_username = os.getenv("ELKS_API_USER")
    api_password = os.getenv("ELKS_API_PASSWORD")
    from_number = os.getenv("ELKS_FROM_NUMBER")

    voice_start = {
        "say": f"A user wants to reserve {medicine_name}. Please confirm."
    }

    response = requests.post(
        "https://api.46elks.com/a1/Calls",
        auth=(api_username, api_password),
        data={
            "from": from_number,
            "to": to_number,
            "voice_start": str(voice_start)
        }
    )

    if response.status_code == 200:
        return response.json().get("id", "Call placed successfully")
    else:
        return f"Failed to place call: {response.status_code} - {response.text}"

