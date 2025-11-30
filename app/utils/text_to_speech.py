import openai
import os
from typing import Optional
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
import io

load_dotenv()

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

async def generate_parallel_audio_files(texts: list, prefix: str = "audio") -> list:
    """
    Generate TTS audio files for multiple texts in parallel
    
    Args:
        texts: List of text strings to convert to speech
        prefix: Prefix for the generated filenames
        
    Returns:
        List of file paths to generated audio files
    """
    import asyncio
    from pathlib import Path
    
    async def create_single_audio_file(text: str, index: int) -> str:
        """Create a single TTS audio file"""
        try:
            result = await convert_text_to_speech(text)
            
            if not result["success"]:
                print(f"TTS failed for {prefix} {index}: {result['message']}")
                return None

            temp_dir = Path("temp_audio")
            temp_dir.mkdir(exist_ok=True)
            
            filename = f"{prefix}_{index}_{hash(text) % 10000}.mp3"
            file_path = temp_dir / filename

            with open(file_path, "wb") as f:
                f.write(result["audio"].getvalue())
            
            domain = os.getenv("DOMAIN")
            if domain:
                return f"{domain}/temp_audio/{filename}"
            else:
                host = os.getenv("API_HOST", "127.0.0.1")
                port = os.getenv("API_PORT", "8061")
                return f"http://{host}:{port}/temp_audio/{filename}"
            
        except Exception as e:
            print(f"Error creating audio file for {prefix} {index}: {e}")
            return None
    
    tasks = [create_single_audio_file(text, i) for i, text in enumerate(texts)]
    audio_files = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [file_path for file_path in audio_files if isinstance(file_path, str)]
