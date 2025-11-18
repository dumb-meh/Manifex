import os
from openai import OpenAI
from app.services.Presentation.context_spin.context_spin_schema import ContextSpinRequest, ContextSpinResponse
import json


class ContextSpin:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def generate_context_spin(self, input: ContextSpinRequest) -> ContextSpinResponse:
        prompt = self.create_prompt(input)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: ContextSpinRequest) -> str:
        prompt = """a"""
        
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> ContextSpinResponse:
        try:
            parsed_data = json.loads(response)
            return ContextSpinResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return ContextSpinResponse()
        except Exception as e:
            print(f"Error creating ContextSpinResponse: {e}")
            return ContextSpinResponse()
        