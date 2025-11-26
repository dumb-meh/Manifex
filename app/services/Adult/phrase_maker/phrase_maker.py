import os
import random
from openai import OpenAI
from app.services.Adult.phrase_maker.phrase_maker_schema import PhraseMakerResponse, PhraseItem
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
        prompt = """
        You are an English learning coach. Create exactly 5 PHRASES (NOT sentences) for vocabulary building exercises.
        
        STRICT REQUIREMENTS:
        - Generate PHRASES only (noun phrases, verb phrases, prepositional phrases)
        - DO NOT generate complete sentences (no subject + predicate combinations)
        - Each phrase should be 2-5 words long
        - Focus on common English phrases that learners should know
        - NO punctuation, articles should be minimal
        - Examples of GOOD phrases: "under the bridge", "very important", "in the morning", "red sports car", "extremely difficult"
        - Examples of BAD phrases (these are sentences): "I go to work", "She is happy", "They were running"
        
        Valid phrase types:
        - Noun phrases: "big red car", "my best friend" 
        - Prepositional phrases: "in the park", "under the table"
        - Adjective phrases: "very tall", "extremely beautiful"
        - Verb phrases: "running fast", "sleeping peacefully"
        - Adverb phrases: "very quickly", "quite often"
        
        Return ONLY a JSON object in this exact format: in the phrase, you will write the phrase and in phrase_options, you will split the phrase into individual words.
        {
            "phrases": [
                {"phrase": "under the bridge", "phrase_options": ["under", "the", "bridge"]},
                {"phrase": "very important", "phrase_options": ["very", "important"]},
                {"phrase": "red sports car", "phrase_options": ["red", "sports", "car"]},
                {"phrase": "in the morning", "phrase_options": ["in", "the", "morning"]},
                {"phrase": "extremely difficult", "phrase_options": ["extremely", "difficult"]}
            ]
        }
        
        Do not include any additional text, explanations, or formatting."""
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
            phrases_data = parsed_data.get('phrases', [])
            
            # Convert each phrase dict to PhraseItem
            phrase_items = []
            for phrase_dict in phrases_data:
                if isinstance(phrase_dict, dict) and 'phrase' in phrase_dict and 'phrase_options' in phrase_dict:
                    # Shuffle the phrase options for the exercise
                    shuffled_options = phrase_dict['phrase_options'].copy()
                    random.shuffle(shuffled_options)
                    
                    phrase_items.append(PhraseItem(
                        phrase=phrase_dict['phrase'],
                        phrase_options=shuffled_options
                    ))
            
            return PhraseMakerResponse(phrases=phrase_items)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhraseMakerResponse()
        except Exception as e:
            print(f"Error creating PhraseMakerResponse: {e}")
            return PhraseMakerResponse()