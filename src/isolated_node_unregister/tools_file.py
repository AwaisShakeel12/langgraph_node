from langchain_core.tools import tool
import requests

FASTAPI_BASE_URL = "http://127.0.0.1:8000"


@tool
def call_register_user(_: str = "") -> dict:
    """Call the FastAPI endpoint to register a new user."""
    try:
        response = requests.post(f"{FASTAPI_BASE_URL}/register-user")
        if response.status_code == 200:
            data = response.json()
            print("✅ User registered via FastAPI")
            print(data["user_id"],  data["status"])
            return {"user_id": data["user_id"], "status": data["status"]}
        else:
            return {"error": "Failed to register user"}
    except Exception as e:
        return {"error": str(e)}

@tool
def call_confirm_registration(user_id: str) -> dict:
    """Call the FastAPI endpoint to confirm if user's account is created."""
    try:
        print(user_id)
        response = requests.get(f"{FASTAPI_BASE_URL}/confirm_registration", params={"user_id": user_id})
        if response.status_code == 200:
            data = response.json()
            print('the confirmation tools working')
            return {"user_id": user_id, "account_created": data.get("account_created", False)}
        else:
            return {"error": "Failed to confirm registration"}
    except Exception as e:
        return {"error": str(e)}