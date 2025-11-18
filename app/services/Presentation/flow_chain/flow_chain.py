import os
from openai import OpenAI
from app.services.Presentation.flow_chain.flow_chain_schema import FlowChainRequest, FlowChainResponse
import json


class FlowChain:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def generate_flow_chain(self, input: FlowChainRequest) -> FlowChainResponse:
        prompt = self.create_prompt(input)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: FlowChainRequest) -> str:
        prompt = """a"""
        
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> FlowChainRequest:
        try:
            parsed_data = json.loads(response)
            return FlowChainResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return FlowChainRequest()
        except Exception as e:
            print(f"Error creating FlowChainResponse: {e}")
            return FlowChainResponse()
        