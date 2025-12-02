import os
from openai import OpenAI
from app.services.Adult.phenome_mapping.phenome_mapping_schema import PhenomeMappingResponse, PhenomeMappingItem
from app.utils.text_to_speech import generate_parallel_audio_files
import json
import re


class PhenomeMapping:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.exercise_cache = []  # Store last 5 exercises
        
    async def get_phenome_mapping(self) -> PhenomeMappingResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        print(f"Raw OpenAI response: {response}")
        
        try:
            # Simple JSON cleaning
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            parsed_response = json.loads(cleaned)
            exercises_data = parsed_response.get('exercises', [])
            
            # Extract all words for audio generation
            words = [exercise.get('word', '') for exercise in exercises_data]
            
            # Generate audio for all words in parallel
            audio_files = await generate_parallel_audio_files(words, "word")
            
            # Create exercise items with audio URLs
            exercises = []
            for i, exercise_data in enumerate(exercises_data):
                word = exercise_data.get('word', '')
                options = exercise_data.get('options', [])
                word_url = audio_files[i] if i < len(audio_files) and audio_files[i] else ""
                
                exercises.append(PhenomeMappingItem(
                    word=word,
                    word_url=word_url,
                    options=options
                ))
            
            # Update cache with new response (keep last 5 responses)
            response_words = [ex.word for ex in exercises]
            print(f"DEBUG: New response words: {response_words}")
            print(f"DEBUG: Cache before update: {self.exercise_cache}")
            self.exercise_cache.append(response_words)  # Store complete response
            self.exercise_cache = self.exercise_cache[-5:]  # Keep only last 5 responses
            print(f"DEBUG: Cache after update: {self.exercise_cache}")
            
            return PhenomeMappingResponse(exercises=exercises)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhenomeMappingResponse(exercises=[])
        except Exception as e:
            print(f"Unexpected error in phenome mapping: {e}")
            return PhenomeMappingResponse(exercises=[])
    

        
    
    def create_prompt(self) -> str:
        # Create exclusion list from cache (flatten all previous responses)
        print(f"DEBUG: Current exercise_cache: {self.exercise_cache}")
        excluded_words = "should, apple, think, green, catch, cat, dog, run, jump, play"
        if self.exercise_cache:
            # Flatten all cached responses into one list
            cached_words = [word for response in self.exercise_cache for word in response]
            excluded_words += ", " + ", ".join(cached_words)
        print(f"DEBUG: Excluded words list: {excluded_words}")
        
        prompt = f"""
        ⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        
        You are an expert phonics instructor creating phoneme mapping exercises.
        
        Generate 5 words for phoneme mapping practice.
        
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!
        
        For each word, provide:
        1. The target word
        2. 6-7 phoneme options that include both correct segments AND similar-sounding distractors
        
        Example format:
        - Word "should" → options: ["sh", "ch", "ou", "ow", "ld", "nd", "s"]
        - Word "apple" → options: ["ap", "p", "le", "b", "ple", "a", "lp"]
        
        Requirements:
        - Mix correct phonemes with similar-sounding distractors
        - Use clear, pronounceable segments
        - Be creative and avoid the excluded words!
        
        Return ONLY this JSON format:
        {{
            "exercises": [
                {{"word": "example", "options": ["ex", "ek", "am", "em", "ple", "pel", "ing"]}}
            ]
        }}
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}],
            temperature=0.7,  
            top_p=0.8,        
            frequency_penalty=0.2, 
            presence_penalty=0.1   
        )
        return response.choices[0].message.content
    

    
    