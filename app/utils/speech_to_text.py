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
        # rewind and log file info
        await audio_file.seek(0)
        try:
            # read bytes to compute size (do not consume permanently)
            file_obj = audio_file.file
            current_pos = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(current_pos)
        except Exception:
            size = None
        print(f"[convert_audio_to_text] received file='{audio_file.filename}' size={size} bytes")

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file.file,
            language=language
        )
        text = transcript.text if hasattr(transcript, 'text') else ''
        print(f"[convert_audio_to_text] raw transcript='{text}'")
        if not text or not text.strip():
            print("[convert_audio_to_text] WARNING: transcript empty or whitespace (possible silent audio)")

        return {
            "text": text,
            "success": True,
            "message": "Audio successfully converted to text"
        }
        
    except Exception as e:
        print(f"[convert_audio_to_text] ERROR: {e}")
        return {
            "text": "",
            "success": False,
            "message": f"Error converting audio to text: {str(e)}"
        }
    
  