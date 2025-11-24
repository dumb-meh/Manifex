import os
from openai import OpenAI
from app.services.Adult.phrase_maker.phrase_maker_schema import PhraseMakerResponse
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
        
        Return ONLY a JSON object in this exact format:
        {
            "phrases": [
                ["under", "the", "bridge"],
                ["very", "important"],
                ["red", "sports", "car"],
                ["in", "the", "morning"],
                ["extremely", "difficult"]
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
            return PhraseMakerResponse(
                phrases=parsed_data.get('phrases', [])
            )
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhraseMakerResponse()
        except Exception as e:
            print(f"Error creating PhraseMakerResponse: {e}")
            return PhraseMakerResponse()