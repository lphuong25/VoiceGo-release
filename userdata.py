import requests
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
}

# create user function
def create_user(username, password):
    password_hash = generate_password_hash(password)
    url = f"{SUPABASE_URL}/rest/v1/users"
    payload = {"username": username, "password_hash": password_hash}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# authenticate user function
def authenticate_user(username, password):
    url = f"{SUPABASE_URL}/rest/v1/users?username=eq.{username}"
    response = requests.get(url,headers=headers)
    data = response.json()
    if data and check_password_hash(data[0]["password_hash"], password):
        return data[0]["id"]
    return None

def save_user_data (user_id, transcription, translation, vocabulary_list):
    url = f"{SUPABASE_URL}/rest/v1/saved_data"
    payload = {
        "user_id": user_id,
        "transcription": transcription,
        "translation": translation,
        "vocabulary_list": vocabulary_list
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def get_user_data(user_id):
    url = f"{SUPABASE_URL}/rest/v1/saved_data?user_id=eq.{user_id}"
    response = requests.get(url, headers=headers)
    return response.json()
