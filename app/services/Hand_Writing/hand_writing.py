import os
import base64
import uuid
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from app.services.Hand_Writing.hand_writing_schema import HandWritingResponse
from fastapi import UploadFile


class HandWritingChecker:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
        # Create test_images directory if it doesn't exist
        self.test_images_dir = Path("test_images")
        self.test_images_dir.mkdir(exist_ok=True)
        
    async def check_handwriting(self, image_file: UploadFile, word: str) -> HandWritingResponse:
        """
        Check if the handwritten text in the image matches the provided word
        """
        try:
            # Read and encode the image
            image_data = await image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Determine image format
            content_type = image_file.content_type or "image/jpeg"
            
            # Create prompt for GPT-4 Vision
            prompt = f"""
            Analyze this image and extract any handwritten text you can see.
            
            Then compare the extracted text with this word: "{word}"
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "matches": true or false
            }}
            
            The match should be case-insensitive and ignore minor spelling variations if the intent is clear.
            """
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Parse the response
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            import json
            result = json.loads(result_text)
            
            matches = result.get('matches', False)
            
            # Save image to test folder for debugging
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_extension = Path(image_file.filename).suffix or ".jpg"
            filename = f"handwriting_{timestamp}_{unique_id}{file_extension}"
            filepath = self.test_images_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            # Generate accessible URL
            image_url = f"/test_images/{filename}"
            
            return HandWritingResponse(correct=matches, image_url=image_url)
            
        except Exception as e:
            print(f"Error checking handwriting: {e}")
            return HandWritingResponse(correct=False)
    

        
    
    