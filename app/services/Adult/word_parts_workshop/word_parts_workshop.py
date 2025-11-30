import os
import random
import datetime
from openai import OpenAI
from app.services.Adult.word_parts_workshop.word_parts_workshop_schema import WordPartsResponse
import json
import re


class WordPartsWorkshop:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def get_word_parts(self) -> WordPartsResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self) -> str:
        session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        example_count = random.choice([3, 4, 5])
        
        # Dynamic word themes
        themes = [
            "academic and educational terms", "medical and health words", 
            "technology and science terms", "business and professional words",
            "psychology and social terms", "environmental and nature words"
        ]
        theme = random.choice(themes)
        
        # Dynamic prefix focus
        prefix_focus = [
            "negative prefixes (un-, dis-, in-)", "movement prefixes (pre-, post-, re-)",
            "quantity prefixes (over-, under-, multi-)", "time prefixes (pre-, post-, ex-)"
        ]
        focus = random.choice(prefix_focus)
        
        prompt = f"""
        You are a vocabulary building expert creating fresh word parts exercises.
        
        Generate {example_count} DIFFERENT word part sets focusing on {theme}.
        
        IMPORTANT: Do NOT use these common examples: "unhappiness", "reaction", "action", "happiness"
        
        Requirements:
        - Focus on {focus}
        - Create word parts from {theme}
        - Use words students would actually encounter
        - Each set should have prefix, root, and suffix components
        - Provide clear, simple meanings for each part
        - Be creative with fresh vocabulary!
        
        Return ONLY valid JSON format:
        {{
            "prefix": ["prefix1", "prefix2", "prefix3"],
            "root": ["root1", "root2", "root3"], 
            "suffix": ["suffix1", "suffix2", "suffix3"],
            "prefix_meaning": ["meaning1", "meaning2", "meaning3"],
            "root_meaning": ["meaning1", "meaning2", "meaning3"],
            "suffix_meaning": ["meaning1", "meaning2", "meaning3"]
        }}
        
        Session: {session_id} | Theme: {theme} | Focus: {focus}
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}],
            temperature=0.7,  # Balanced creativity with JSON structure
            top_p=0.8,        # More focused sampling
            frequency_penalty=0.2,  # Gentle penalty to avoid repetition
            presence_penalty=0.1    # Light penalty for topic diversity
        )
        return response.choices[0].message.content
    
    def clean_json_response(self, response: str) -> str:
        """Clean and repair common JSON formatting issues."""
        cleaned = response.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        start = cleaned.find('{')
        if start == -1:
            return cleaned
        
        brace_count = 0
        end = start
        for i, char in enumerate(cleaned[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        if end > start:
            cleaned = cleaned[start:end]
        
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
        return cleaned
    
    def format_response(self, response: str) -> WordPartsResponse:
        try:
            cleaned_response = self.clean_json_response(response)
            parsed_data = json.loads(cleaned_response)
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
        
