import os
from openai import OpenAI
from app.services.Adult.word_flash.word_flash_schema import WordFlashRequest, WordFlashResponse
import json


class WordFlash:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def word_flash_score(self,input:WordFlashRequest, transcript) -> WordFlashResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:WordFlashRequest, transcript) -> str:
        prompt = f"""
        You are an expert speaking practice coach.
        you will recive the following by:
        word: {input.word}
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
    
    def format_response(self, response: str) -> WordFlashResponse:
        try:
            parsed_data = json.loads(response)
            return WordFlashResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return WordFlashResponse()
        except Exception as e:
            print(f"Error creating WordFlashResponse: {e}")
            return WordFlashResponse()
        
    def generate_word_flash(self, age) -> dict:
        prompt = f"""You are expert speaking coach. In order to improve speaking skills, you will provide a list of 5 challenging words.
        
        Return ONLY a JSON object in this exact format:
        {{
            "words": ["word1", "word2", "word3", "word4", "word5"]
        }}
        
        Do not include any additional text or formatting."""
        response = self.get_openai_response(prompt)
        try:
            parsed_response = json.loads(response)
            words = parsed_response.get('words', [])
            
            return {
                "words": words
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"words": []}