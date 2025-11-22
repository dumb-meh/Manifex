import os
from openai import OpenAI
from app.services.Adult.sentence_builder.sentence_builder_schema import SentenceBuilderResponse
import json


class SentenceBuilder:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def get_sentences(self) -> SentenceBuilderResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self) -> str:
        prompt = f"""
        You are an English learning coach. Create 5 sentences using different words. For each sentence, return it as a list of words that will be used to shuffle and build sentences. 
        Return ONLY a JSON object in this exact format:
        {{
            "sentences": [["I", "am", "happy", "to", "see", "you"], ["She", "is", "running", "to", "school"]]
        }}
        
        Do not include any additional text or formatting."""
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> SentenceBuilderResponse:
        try:
            parsed_data = json.loads(response)
            return SentenceBuilderResponse(
                sentences=parsed_data.get('sentences', [])
            )
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return SentenceBuilderResponse()
        except Exception as e:
            print(f"Error creating SentenceBuilderResponse: {e}")
            return SentenceBuilderResponse()
        
