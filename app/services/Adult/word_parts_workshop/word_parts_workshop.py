import os
from openai import OpenAI
from app.services.Adult.word_parts_workshop.word_parts_workshop_schema import WordPartsResponse
import json
import re


class WordPartsWorkshop:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.word_cache = []  # Store last 5 words
        
    def get_word_parts(self) -> WordPartsResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self) -> str:
        # Create exclusion list from cache (flatten all previous responses)
        excluded_words = "unhappiness, reaction, action, happiness"
        if self.word_cache:
            # Flatten all cached responses into one list
            cached_words = [word for response in self.word_cache for word in response]
            excluded_words += ", " + ", ".join(cached_words)
        
        prompt = f"""
        ⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        
        You are a vocabulary building expert creating fresh word parts exercises.
        
        Generate 3 DIFFERENT word part sets.
        
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!
        
        Requirements:
        - Each set should have prefix, root, and suffix components
        - Use words students would actually encounter
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
    

    
    def format_response(self, response: str) -> WordPartsResponse:
        try:
            # Simple JSON cleaning
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            parsed_data = json.loads(cleaned)
            
            # Update cache with new response (keep last 5 responses)
            response_words = parsed_data.get('prefix', []) + parsed_data.get('root', []) + parsed_data.get('suffix', [])
            self.word_cache.append(response_words)  # Store complete response
            self.word_cache = self.word_cache[-5:]  # Keep only last 5 responses
            
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
        
