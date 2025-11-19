import os
from openai import OpenAI
from app.services.Presentation.context_spin.context_spin_schema import ContextSpinRequest, ContextSpinResponse
import json


class ContextSpin:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def context_spin_score(self,input:ContextSpinRequest, transcript) -> ContextSpinResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:ContextSpinRequest, transcript) -> str:
        prompt = f"""
        You are an expert presentation coach. Evaluate the following text based on its context relevance and vocabulary integration.
        you will recive the following by:
        score each aspect on a scale of 1-10 and provide constructive feedback and suggestions for improvement
        The json response must be exactly in this format
        {{
            "score": 8,
            "feedback": ""
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
        
    def context_spin_score(self) -> list:
        prompt = f"""You are expert presentation coach. In order to improve spontaneous verbal thinking and vocabulary integration. Give 5 key vocabulary words and 5 random scenarios (e.g., “at a press conference,” “during a TED talk,” “motivating your team”)
        return a json in the following format:
        {{
            "words": [word1, word2, word3, word4, word5],
            "scenario": secnario
        }}"""
        response = self.get_openai_response(prompt)
        return self.format_response(response)