import os
from openai import OpenAI
from app.services.Presentation.precision_drill.precision_drill_schema import PrecisionDrillRequest, PrecisionDrillResponse
import json


class PrecisionDrill:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def precision_drill(self, input: PrecisionDrillRequest) -> PrecisionDrillResponse:
        prompt = self.create_prompt(input)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: PrecisionDrillRequest) -> str:
        prompt = """a"""
        
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> PrecisionDrillResponse:
        try:
            parsed_data = json.loads(response)
            return PrecisionDrillResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PrecisionDrillResponse()
        except Exception as e:
            print(f"Error creating PrecisionDrillResponse: {e}")
            return PrecisionDrillResponse()
        