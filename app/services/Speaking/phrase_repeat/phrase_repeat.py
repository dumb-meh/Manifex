import os
from openai import OpenAI
from app.services.Speaking.phrase_repeat.phrase_repeat_schema import PhraseRepeatRequest, PhraseRepeatResponse
from app.utils.text_to_speech import generate_parallel_audio_files
import json


class PhraseRepeat:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def phrase_repeat_score(self,input:PhraseRepeatRequest, transcript) -> PhraseRepeatResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:PhraseRepeatRequest, transcript) -> str:
        prompt = f"""
        You are an expert speaking coach. Evaluate the user's pronunciation based on the following criteria: clarity, fluency, intonation, and overall effectiveness in conveying the intended message.
        you will recive the following by:
        phrase_list: {input.phrase_list}
        user transcript: {transcript}
        score each aspect on a scale of 1-10 and provide constructive feedback and suggestions for improvement
        The json response must be exactly in this format
        {{
            "score": 8,
            "feedback": "One liner feedback",
            "status": "success",
            "message": "Evaluation completed successfully."

        }}
        
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> PhraseRepeatResponse:
        try:
            parsed_data = json.loads(response)
            return PhraseRepeatResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhraseRepeatResponse()
        except Exception as e:
            print(f"Error creating ContextSpinResponse: {e}")
            return PhraseRepeatResponse()
        
    async def generate_phrase_repeat(self, age) -> dict:
        prompt = f"""You are expert speaking coach. Generate a list of 5 phrases that are moderately challenging to pronounce but still commonly used in everyday conversations based on the user's age. These phrases should help improve diction and fluency when practiced.
        
        User age: {age}
        Return ONLY a JSON object in this exact format:
        {{
            "phrases": ["phrase1", "phrase2", "phrase3", "phrase4", "phrase5"]
        }}
        
        Do not include any additional text or formatting."""
        response = self.get_openai_response(prompt)
        try:
            parsed_response = json.loads(response)
            phrases = parsed_response.get('phrases', [])
            
            # Generate TTS audio files in parallel for all phrases
            audio_files = await generate_parallel_audio_files(phrases, "phrase")
            
            return {
                "phrases": phrases,
                "audio_files": audio_files
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"phrases": [], "audio_files": []}