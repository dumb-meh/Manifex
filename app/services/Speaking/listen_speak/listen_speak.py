import os
from openai import OpenAI
from app.services.Speaking.listen_speak.listen_speak_schema import ListenSpeakRequest, ListenSpeakResponse
from app.utils.text_to_speech import generate_parallel_audio_files
import json


class ListenSpeak:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def listen_speak_score(self,input:ListenSpeakRequest, transcript) -> ListenSpeakResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:ListenSpeakRequest, transcript) -> str:
        prompt = f"""
        You are an expert speaking practice coach.
        you will recive the following by:
        senetence: {input.sentence}
        user transcript: {transcript}
        score each aspect on a scale of 1-10 and provide constructive feedback and suggestions for improvement
        The json response must be exactly in this format
        {{
            "score": 8,
            "feedback": "One liner feedback such as "great pronunciation","try better next time",
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
    
    def format_response(self, response: str) -> ListenSpeakResponse:
        try:
            parsed_data = json.loads(response)
            return ListenSpeakResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return ListenSpeakResponse()
        except Exception as e:
            print(f"Error creating ListenSpeakResponse: {e}")
            return ListenSpeakResponse()
        
    async def generate_listen_speak(self, age) -> dict:
        prompt = f"""You are expert speaking coach. In order to improve speaking skills, you will provide a list of 5 challenging sentences based on their age. User age is {age}.
        
        Return ONLY a JSON object in this exact format:
        {{
            "sentences": ["sentence1", "sentence2", "sentence3", "sentence4", "sentence5"]
        }}
        
        Do not include any additional text or formatting."""
        response = self.get_openai_response(prompt)
        try:
            parsed_response = json.loads(response)
            sentences = parsed_response.get('sentences', [])
            
            # Generate TTS audio files in parallel using the reusable utility function
            audio_files = await generate_parallel_audio_files(sentences, "sentence")
            
            return {
                "sentences": sentences,
                "audio_files": audio_files
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"sentences": [], "audio_files": []}