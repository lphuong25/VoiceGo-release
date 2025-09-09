import whisper

model = whisper.load_model("base")

def transcribe_audio(file_path: str, language: str = "ja"):

    result = model.transcribe(file_path, language=language)

    return result["text"]


    
    