from fastapi import FastAPI, UploadFile, File, Request, Form, HTTPException
from fastapi.responses import JSONResponse
import os
from pydantic import BaseModel
from typing import Dict, List, Any
from transcription import transcribe_audio
from translation import translate
from vocabulary import tokenize_word, vocabulary_extraction
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from userdata import create_user, authenticate_user, save_user_data, get_user_data

app = FastAPI()

app.mount("/static", StaticFiles(directory = "static"), name = "static")
templates = Jinja2Templates(directory = "templates")

# Upload directory for audio files
UPLOAD_DIR = "uploads"
# Check the if the directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint to upload audio file
@app.post("/uploads")
async def upload_audio(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open (file_path, "wb") as f:
        f.write(await file.read())

    transcription = transcribe_audio(file_path)
    translation = translate(transcription)
    tokenized_words = tokenize_word(transcription)
    vocabulary_list = vocabulary_extraction(tokenized_words)

    # Return file name and transcription result
    return {
        "filename": file.filename,
        "transcription": transcription,
        "translation": translation,
        # remember to change the word with the actual English translation
        #"vocabulary extraction": tokenized_words,
        "vocabulary_list": vocabulary_list
    }
    
@app.get("/flashcard")
def flashcard(request: Request):
    return templates.TemplateResponse("flashcard.html", {"request": request})

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    try:
        result = create_user(username, password)
        # Check if user creation is success
        if result:    
            return {"message": "User registered successfully"}
        return {"error": "User registration failed"}
    except Exception as e:
        return {"error": f"Registration failed: {str(e)}"}

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    try:
        user_id = authenticate_user(username, password)
        if user_id:
            return {"message": "Login successful", "user_id": user_id}
        return {"error": "Invalid username or password"}
    except Exception as e:
        return {"error": f"Login failed: {str(e)}"}

class UserDataModel(BaseModel):
    user_id: int
    transcription: str
    translation: str
    vocabulary_list: Dict[str, List[Dict[str, Any]]]
    
# endpoint to save user data
@app.post("/save_user_data")
async def save_user_data_endpoint(user_data: UserDataModel):
    try:
        result = await save_user_data(
            user_data.user_id,
            user_data.transcription,
            user_data.translation,
            user_data.vocabulary_list
        )
        return {"message": "User data saved successfully"}
    except Exception as e:
        return {"error": f"Failed to save user data: {str(e)}"}
    
# endpoint to get user data
@app.get("/get_user_data/{user_id}")
async def get_user_data_endpoint(user_id: str):
    try:
        user_data = await get_user_data(user_id)
        return {"user_data": user_data}
    except Exception as e:
        return {"error": f"Failed to get user data: {str(e)}"}
    
    