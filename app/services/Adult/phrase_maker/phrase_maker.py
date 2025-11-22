import os
from openai import OpenAI
from app.services.Adult.phrase_maker.phrase_maker_schema import PhraseMakerResponse
import json


class PhraseMaker:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def get_phrases(self) -> PhraseMakerResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self) -> str:
        prompt = f"""
        You are an English learning coach. Create 5 phrases using different words. For each phrase, return it as a list of words that will be used to shuffle and build phrases. 
        Return ONLY a JSON object in this exact format:
        {{
            "phrases": [["go", "to", "work"], ["deep","in","thought"]]
        }}
        
        Do not include any additional text or formatting."""
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> PhraseMakerResponse:
        try:
            parsed_data = json.loads(response)
            return PhraseMakerResponse(
                phrases=parsed_data.get('phrases', [])
            )
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhraseMakerResponse()
        except Exception as e:
            print(f"Error creating PhraseMakerResponse: {e}")
            return PhraseMakerResponse()