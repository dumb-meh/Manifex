import os
from openai import OpenAI
from app.services.Adult.word_parts_workshop.word_parts_workshop_schema import WordPartsResponse
import json


class WordPartsWorkshop:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def word_parts_score(self) -> WordPartsResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self) -> str:
        prompt = f"""
        You are an English learning coach. Teach how to create word parts such as prefixes, roots, and suffixes. 
        return in json format.
        for example if the word is "unhappiness", the prefix is "un", root is "happy", suffix is "ness".
        {{
            "prefix": ["re","un"],
            "root": ["act","un"],
            "suffix": ["tion","ness"],
            "prefix_meaning": ["again","not"],
            "root_meaning": ["to do","not"],
            "suffix_meaning": ["the act of","state of"]

        }}
        
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> WordPartsResponse:
        try:
            parsed_data = json.loads(response)
            return WordPartsResponse(
                prefix=parsed_data.get('prefix', []),
                root=parsed_data.get('root', []),
                suffix=parsed_data.get('suffix', []),
                prefix_meaning=parsed_data.get('prefix_meaning', []),
                root_meaning=parsed_data.get('root_meaning', []),
                suffix_meaning=parsed_data.get('suffix_meaning', [])
            )
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return WordPartsResponse()
        except Exception as e:
            print(f"Error creating WordPartsResponse: {e}")
            return WordPartsResponse()
        
