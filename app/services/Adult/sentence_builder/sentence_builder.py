import os
from openai import OpenAI
from app.services.Adult.sentence_builder.sentence_builder_schema import SentenceBuilderResponse, SentenceItem
import json
import re


class SentenceBuilder:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.sentence_cache = []  # Store last 5 sentences
        
    def get_sentences(self) -> SentenceBuilderResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self) -> str:
        # Create exclusion list from cache
        excluded_sentences = "I love reading books, The cat is sleeping, Where are you going?, She runs very fast, We eat dinner together"
        if self.sentence_cache:
            excluded_sentences += ", " + ", ".join(self.sentence_cache)
        
        prompt = f"""
        You are an English grammar instructor creating fresh sentence building exercises.
        
        Generate 5 COMPLETELY NEW sentences. 
        
        CRITICAL: Do NOT use ANY of these sentences (recently used or overused): {excluded_sentences}
        
        Requirements:
        - Mix different tenses and sentence types
        - Each sentence 4-8 words long
        - Be creative and original!
        
        For each sentence provide:
        1. Complete correct sentence
        2. Words split for shuffling - ATTACH punctuation to the final word (e.g., "going?" not "going", "?")
        
        CRITICAL: Do NOT create separate entries for punctuation marks like periods, question marks, or exclamation points.
        
        Examples of CORRECT format:
        - Sentence: "Where are you going?" → Options: ["Where", "are", "you", "going?"]  
        - Sentence: "I love pizza." → Options: ["I", "love", "pizza."]
        - Sentence: "Help me now!" → Options: ["Help", "me", "now!"]
        
        Return ONLY valid JSON:
        {{
            "sentences": [
                {{"sentence": "example sentence here", "sentence_options": ["example", "sentence", "here"]}},
                {{"sentence": "another example sentence", "sentence_options": ["another", "example", "sentence"]}}
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
    

    
    def format_response(self, response: str) -> SentenceBuilderResponse:
        try:
            # Simple JSON cleaning
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            parsed_data = json.loads(cleaned)
            sentences_data = parsed_data.get('sentences', [])
            
            # Convert each sentence dict to SentenceItem
            sentence_items = []
            new_sentences = []
            for sentence_dict in sentences_data:
                if isinstance(sentence_dict, dict) and 'sentence' in sentence_dict and 'sentence_options' in sentence_dict:
                    sentence_text = sentence_dict['sentence']
                    new_sentences.append(sentence_text)
                    
                    # Clean up sentence options - merge standalone punctuation with previous word
                    options = sentence_dict['sentence_options'].copy()
                    cleaned_options = []
                    
                    for i, option in enumerate(options):
                        # If this option is just punctuation and there's a previous word
                        if option.strip() in ['.', '?', '!', ',', ';', ':'] and cleaned_options:
                            # Attach punctuation to the last word
                            cleaned_options[-1] += option.strip()
                        else:
                            cleaned_options.append(option)
                    
                    sentence_items.append(SentenceItem(
                        sentence=sentence_text,
                        sentence_options=cleaned_options
                    ))
            
            # Update cache with new sentences (keep last 5)
            self.sentence_cache.extend(new_sentences)
            self.sentence_cache = self.sentence_cache[-5:]
            
            return SentenceBuilderResponse(sentences=sentence_items)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return SentenceBuilderResponse()
        except Exception as e:
            print(f"Error creating SentenceBuilderResponse: {e}")
            return SentenceBuilderResponse()
        
