import openai
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
import io

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def convert_text_to_speech(text: str, voice: Optional[str] = "alloy") -> dict:
    """
    Convert text to speech using OpenAI TTS
    
    Args:
        text: Text to convert to speech
        voice: Optional voice selection (alloy, echo, fable, onyx, nova, shimmer)
        
    Returns:
        Dictionary with audio data and success status
    """
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        # Create a BytesIO object to store the audio data
        audio_buffer = io.BytesIO()
        for chunk in response.iter_bytes():
            audio_buffer.write(chunk)
        audio_buffer.seek(0)
        
        return {
            "audio": audio_buffer,
            "success": True,
            "message": "Text successfully converted to speech"
        }
        
    except Exception as e:
        return {
            "audio": None,
            "success": False,
            "message": f"Error converting text to speech: {str(e)}"
        }

def create_audio_response(audio_buffer: io.BytesIO) -> StreamingResponse:
    """
    Create a streaming response for audio playback
    
    Args:
        audio_buffer: BytesIO object containing audio data
        
    Returns:
        StreamingResponse for audio playback
    """
    return StreamingResponse(
        io.BytesIO(audio_buffer.read()),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=speech.mp3"}
    )
