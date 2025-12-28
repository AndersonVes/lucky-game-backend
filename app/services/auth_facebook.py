import requests
from app.core.config import settings

def validate_facebook_token(token: str):
    app_token = f"{settings.FB_APP_ID}|{settings.FB_APP_SECRET}"

    r = requests.get(
        "https://graph.facebook.com/debug_token",
        params={
            "input_token": token,
            "access_token": app_token
        }
    )

    data = r.json().get("data")
    return data if data and data.get("is_valid") else None


def get_facebook_user(token: str):
    r = requests.get(
        "https://graph.facebook.com/me",
        params={
            "fields": "id,name",
            "access_token": token
        }
    )
    return r.json()
