import os
from openai import OpenAI
from app.services.Adult.sentence_builder.sentence_builder_schema import SentenceBuilderResponse, SentenceItem
import json


class SentenceBuilder:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def get_sentences(self) -> SentenceBuilderResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self) -> str:
        prompt = """
        You are an English learning coach. Create exactly 5 sentences for sentence building exercises.
        
        REQUIREMENTS:
        - Generate complete, grammatically correct sentences
        - Use simple to moderate vocabulary
        - Each sentence should be 4-8 words long
        - Focus on common sentence structures
        - Include variety: statements, questions, different tenses
        - Examples: "I love reading books", "The cat is sleeping", "Where are you going?"
        
        For each sentence, provide:
        1. The complete correct sentence
        2. All words from the sentence split into individual words for shuffling
        
        Return ONLY a JSON object in this exact format:
        {
            "sentences": [
                {"sentence": "I love reading books", "sentence_options": ["I", "love", "reading", "books"]},
                {"sentence": "The cat is sleeping", "sentence_options": ["The", "cat", "is", "sleeping"]},
                {"sentence": "Where are you going?", "sentence_options": ["Where", "are", "you", "going?"]},
                {"sentence": "She runs very fast", "sentence_options": ["She", "runs", "very", "fast"]},
                {"sentence": "We eat dinner together", "sentence_options": ["We", "eat", "dinner", "together"]}
            ]
        }
        
        Do not include any additional text or formatting."""
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> SentenceBuilderResponse:
        try:
            parsed_data = json.loads(response)
            sentences_data = parsed_data.get('sentences', [])
            
            # Convert each sentence dict to SentenceItem
            sentence_items = []
            for sentence_dict in sentences_data:
                if isinstance(sentence_dict, dict) and 'sentence' in sentence_dict and 'sentence_options' in sentence_dict:
                    sentence_items.append(SentenceItem(
                        sentence=sentence_dict['sentence'],
                        sentence_options=sentence_dict['sentence_options']
                    ))
            
            return SentenceBuilderResponse(sentences=sentence_items)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return SentenceBuilderResponse()
        except Exception as e:
            print(f"Error creating SentenceBuilderResponse: {e}")
            return SentenceBuilderResponse()
        
