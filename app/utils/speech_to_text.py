import openai
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import UploadFile

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def convert_audio_to_text(audio_file: UploadFile, language: Optional[str] = None) -> dict:
    """
    Convert audio to text using OpenAI Whisper
    
    Args:
        audio_file: Uploaded audio file from FastAPI
        language: Optional language code for recognition
        
    Returns:
        Dictionary with text and success status
    """
    try:
        await audio_file.seek(0)
        
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file.file,
            language=language
        )
        
        return {
            "text": transcript.text,
            "success": True,
            "message": "Audio successfully converted to text"
        }
        
    except Exception as e:
        return {
            "text": "",
            "success": False,
            "message": f"Error converting audio to text: {str(e)}"
        }
    
  