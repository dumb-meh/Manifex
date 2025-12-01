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
            cleaned_response = self.clean_json_response(response)
            parsed_response = json.loads(cleaned_response)
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
            
            # Update cache with new exercises (keep last 5)
            new_words = [ex.word for ex in exercises]
            self.exercise_cache.extend(new_words)
            self.exercise_cache = self.exercise_cache[-5:]  # Keep only last 5
            
            return PhenomeMappingResponse(exercises=exercises)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhenomeMappingResponse(exercises=[])
        except Exception as e:
            print(f"Unexpected error in phenome mapping: {e}")
            return PhenomeMappingResponse(exercises=[])
    

        
    
    def create_prompt(self) -> str:
        # Create exclusion list from cache
        excluded_words = "should, apple, think, green, catch, cat, dog, run, jump, play"
        if self.exercise_cache:
            excluded_words += ", " + ", ".join(self.exercise_cache)
        
        prompt = f"""
        You are an expert phonics instructor creating fresh phoneme mapping exercises. 

        Generate 5 completely NEW and DIFFERENT phoneme mapping exercises.
        
        CRITICAL: Do NOT use ANY of these words (recently used or common): {excluded_words}
        
        Each exercise needs:
        1. A target word (3-6 phonemes)
        2. 6-8 phoneme options mixing correct segments with similar-sounding distractors
        
        Requirements:
        - Break words into clear pronounceable segments (like "str-ong" not "s-t-r-o-n-g")
        - Include 3-4 distractor phonemes that sound similar but incorrect
        - Shuffle correct and incorrect options randomly
        - Use fresh, uncommon words - be creative and avoid the excluded list!
        
        Return ONLY valid JSON format:
        {{{{
            "exercises": [
                {{"word": "example_word", "options": ["ex", "ek", "am", "em", "ple", "pel", "ing"]}},
                {{"word": "another_word", "options": ["an", "en", "oth", "uth", "er", "ar", "word", "werd"]}}
            ]
        }}}}
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}],
            temperature=0.7,  # Lower temperature for better JSON structure
            top_p=0.8,        # More focused sampling
            frequency_penalty=0.2,  # Gentle penalty to avoid repetition
            presence_penalty=0.1    # Light penalty for topic diversity
        )
        return response.choices[0].message.content
    
    def clean_json_response(self, response: str) -> str:
        """Clean and repair common JSON formatting issues."""        
        if not response:
            return '{"exercises": []}'
        
        cleaned = response.strip()
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        start = cleaned.find('{')
        if start == -1:
            return '{"exercises": []}'
        
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
        else:
            # If we can't find proper end, try to construct valid JSON
            if '"exercises"' in cleaned:
                # Try to extract just the exercises array
                exercises_start = cleaned.find('"exercises"')
                if exercises_start != -1:
                    array_start = cleaned.find('[', exercises_start)
                    if array_start != -1:
                        # Try to find array end
                        bracket_count = 0
                        array_end = array_start
                        for i in range(array_start, len(cleaned)):
                            if cleaned[i] == '[':
                                bracket_count += 1
                            elif cleaned[i] == ']':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    array_end = i + 1
                                    break
                        
                        if bracket_count > 0:
                            # Add missing closing brackets
                            cleaned += ']' * bracket_count
                            array_end = len(cleaned)
                        
                        # Extract the array and wrap it
                        array_content = cleaned[array_start:array_end]
                        cleaned = f'{{"exercises": {array_content}}}'
                    else:
                        cleaned = '{"exercises": []}'
                else:
                    cleaned = '{"exercises": []}'
            else:
                cleaned = '{"exercises": []}'
        
        # Remove trailing commas
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
        
        # Fix single quotes to double quotes
        cleaned = re.sub(r"'([^']*)':", r'"\1":', cleaned)
        cleaned = re.sub(r":\s*'([^']*)'", r': "\1"', cleaned)
        
        return cleaned
    
    