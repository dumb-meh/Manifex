import os
from openai import OpenAI
from app.services.Adult.phrase_maker.phrase_maker_schema import PhraseMakerResponse, PhraseItem
import json
import re


class PhraseMaker:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.phrase_cache = []  # Store last 5 phrases
        
    def get_phrases(self) -> PhraseMakerResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self) -> str:
        # Create exclusion list from cache
        excluded_phrases = "under the bridge, very important, in the morning, red sports car, extremely difficult"
        if self.phrase_cache:
            excluded_phrases += ", " + ", ".join(self.phrase_cache)
        
        prompt = f"""
        You are an English vocabulary instructor creating fresh phrase-building exercises.
        
        Generate 5 COMPLETELY NEW phrases (NOT complete sentences).
        
        CRITICAL: Do NOT use ANY of these phrases (recently used or overused): {excluded_phrases}
        
        STRICT REQUIREMENTS:
        - Generate PHRASES only (noun phrases, verb phrases, prepositional phrases)
        - NO complete sentences with subject + verb + object
        - Each phrase 2-5 words long
        - Be creative and use fresh vocabulary!
        
        Phrase types to create:
        - Noun phrases: "[adjective] [noun]" or "[adjective] [adjective] [noun]"
        - Prepositional phrases: "[preposition] [article] [noun]"
        - Verb phrases: "[verb] [adverb]" or "[adverb] [verb]"
        - Descriptive phrases: "[very/quite/extremely] [adjective]"
        
        Return ONLY valid JSON format:
        {{
            "phrases": [
                {{"phrase": "fresh_example_phrase", "phrase_options": ["fresh", "example", "phrase"]}},
                {{"phrase": "another_new_phrase", "phrase_options": ["another", "new", "phrase"]}}
            ]
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
    
    def format_response(self, response: str) -> PhraseMakerResponse:
        try:
            cleaned_response = self.clean_json_response(response)
            parsed_data = json.loads(cleaned_response)
            phrases_data = parsed_data.get('phrases', [])
            
            # Convert each phrase dict to PhraseItem
            phrase_items = []
            new_phrases = []
            for phrase_dict in phrases_data:
                if isinstance(phrase_dict, dict) and 'phrase' in phrase_dict and 'phrase_options' in phrase_dict:
                    phrase_text = phrase_dict['phrase']
                    new_phrases.append(phrase_text)
                    
                    phrase_items.append(PhraseItem(
                        phrase=phrase_text,
                        phrase_options=phrase_dict['phrase_options']
                    ))
            
            # Update cache with new phrases (keep last 5)
            self.phrase_cache.extend(new_phrases)
            self.phrase_cache = self.phrase_cache[-5:]
            
            return PhraseMakerResponse(phrases=phrase_items)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhraseMakerResponse()
        except Exception as e:
            print(f"Error creating PhraseMakerResponse: {e}")
            return PhraseMakerResponse()