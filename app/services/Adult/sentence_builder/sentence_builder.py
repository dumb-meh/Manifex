import os
import random
import datetime
from openai import OpenAI
from app.services.Adult.sentence_builder.sentence_builder_schema import SentenceBuilderResponse, SentenceItem
import json
import re


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
        session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # More unique
        
        # Dynamic focus areas
        grammar_focus = random.choice([
            "simple present tense with action verbs",
            "past tense with regular and irregular verbs", 
            "questions using who, what, where, when, why",
            "negative statements with don't/doesn't/didn't",
            "future tense with will/going to",
            "present continuous with -ing verbs"
        ])
        
        # Dynamic topics for variety
        topics = [
            "daily routines", "hobbies and interests", "family activities", 
            "school life", "weekend plans", "food and cooking",
            "travel and transportation", "weather and seasons", "work and jobs"
        ]
        topic = random.choice(topics)
        
        # Dynamic sentence structures
        structures = [
            "Mix statements, questions, and commands",
            "Include both simple and compound sentences",
            "Vary between short 4-word and longer 8-word sentences",
            "Balance positive and negative statements"
        ]
        structure = random.choice(structures)
        
        prompt = f"""
        You are an English grammar instructor creating fresh sentence building exercises.
        
        Generate 5 COMPLETELY NEW sentences about {topic}. 
        
        IMPORTANT: Avoid these overused examples: "I love reading books", "The cat is sleeping", "Where are you going?", "She runs very fast", "We eat dinner together"
        
        Requirements:
        - Focus on {grammar_focus}
        - {structure}
        - Each sentence 4-8 words long
        - Use vocabulary related to {topic}
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
        
        Session: {session_id} | Grammar: {grammar_focus} | Topic: {topic}
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
    
    def format_response(self, response: str) -> SentenceBuilderResponse:
        try:
            cleaned_response = self.clean_json_response(response)
            parsed_data = json.loads(cleaned_response)
            sentences_data = parsed_data.get('sentences', [])
            
            # Convert each sentence dict to SentenceItem
            sentence_items = []
            for sentence_dict in sentences_data:
                if isinstance(sentence_dict, dict) and 'sentence' in sentence_dict and 'sentence_options' in sentence_dict:
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
                    
                    # Shuffle the cleaned sentence options for the exercise
                    random.shuffle(cleaned_options)
                    
                    sentence_items.append(SentenceItem(
                        sentence=sentence_dict['sentence'],
                        sentence_options=cleaned_options
                    ))
            
            return SentenceBuilderResponse(sentences=sentence_items)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return SentenceBuilderResponse()
        except Exception as e:
            print(f"Error creating SentenceBuilderResponse: {e}")
            return SentenceBuilderResponse()
        
