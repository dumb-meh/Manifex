import os
from openai import OpenAI
from app.services.Adult.phenome_mapping.phenome_mapping_schema import PhenomeMappingResponse, PhenomeMappingItem
from app.utils.text_to_speech import generate_parallel_audio_files
import json
import random
import re


class PhenomeMapping:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.exercise_cache = []  # Store last 10 exercises
    
    def _generate_phoneme_options(self, word: str) -> dict:
        """
        Generate 7-9 substring options where ONLY ONE combination (concatenation) reconstructs the full word.
        Returns {"options": [...], "correct_combination": [indices]}
        
        Example: word="Emaculate" → options=["Ema", "cu", "late", "mac", "em", "cul", "ate"]
                 only combining indices [0,1,2] gives "Emaculate"
        """
        word_lower = word.lower()
        
        # Step 1: Split word into 3-4 correct phonemes (non-overlapping)
        word_len = len(word_lower)
        
        # Decide how many phonemes (3-4)
        num_phonemes = 3 if word_len < 8 else 4
        
        # Simple split strategy: divide word into roughly equal parts
        correct_phonemes = []
        if num_phonemes == 3:
            split1 = word_len // 3
            split2 = (word_len * 2) // 3
            correct_phonemes = [
                word_lower[:split1],
                word_lower[split1:split2],
                word_lower[split2:]
            ]
        else:  # 4 phonemes
            split1 = word_len // 4
            split2 = (word_len * 2) // 4
            split3 = (word_len * 3) // 4
            correct_phonemes = [
                word_lower[:split1],
                word_lower[split1:split2],
                word_lower[split2:split3],
                word_lower[split3:]
            ]
        
        correct_indices = list(range(len(correct_phonemes)))
        
        # Step 2: Generate distractors (substrings that won't combine to form the word)
        distractors = []
        
        # Add substrings of various positions/lengths that break the correct combination
        tried = set(correct_phonemes)  # Don't add correct phonemes
        
        for start in range(len(word_lower)):
            for length in range(2, min(4, len(word_lower) - start + 1)):
                substring = word_lower[start:start + length]
                # Only add if it's not a correct phoneme and we haven't tried it
                if substring not in tried and len(distractors) < 6:
                    # Verify this distractor doesn't accidentally form a complete word when combined
                    distractors.append(substring)
                    tried.add(substring)
        
        # Step 3: Combine correct phonemes + distractors
        all_options = correct_phonemes + distractors
        
        # Shuffle options but track which indices are the correct combination
        index_mapping = {}
        for i, phoneme in enumerate(all_options):
            if phoneme not in index_mapping:
                index_mapping[phoneme] = []
            index_mapping[phoneme].append(i)
        
        shuffled_options = list(all_options)
        random.shuffle(shuffled_options)
        
        # Map old indices to new indices after shuffle
        new_correct_indices = []
        temp_mapping = {phoneme: [] for phoneme in all_options}
        for i, phoneme in enumerate(shuffled_options):
            temp_mapping[phoneme].append(i)
        
        # Find new indices of correct phonemes in shuffled list
        for phoneme in correct_phonemes:
            for idx in temp_mapping[phoneme]:
                if idx not in new_correct_indices:
                    new_correct_indices.append(idx)
                    break
        
        new_correct_indices.sort()  # Keep in order for concatenation
        
        return {
            "options": shuffled_options,
            "correct_combination": new_correct_indices
        }
        
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
            words_data = parsed_response.get('words', [])
            
            # Generate audio for all words in parallel
            audio_files = await generate_parallel_audio_files(words_data, "word")
            
            # Create exercise items with programmatically generated phoneme options
            exercises = []
            for i, word in enumerate(words_data):
                phoneme_data = self._generate_phoneme_options(word)
                word_url = audio_files[i] if i < len(audio_files) and audio_files[i] else ""
                
                exercises.append(PhenomeMappingItem(
                    word=word,
                    word_url=word_url,
                    options=phoneme_data["options"],
                    correct_combination=phoneme_data["correct_combination"]
                ))
            
            # Update cache with new response (keep last 10 responses)
            response_words = [ex.word for ex in exercises]
            print(f"DEBUG: New response words: {response_words}")
            print(f"DEBUG: Cache before update: {self.exercise_cache}")
            self.exercise_cache.append(response_words)  # Store complete response
            self.exercise_cache = self.exercise_cache[-10:]  # Keep only last 10 responses
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
        
        You are an expert phonics instructor. Generate 5 common English words for phoneme mapping practice.
        
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!
        
        Requirements:
        - Use clear, common 4-8 letter words
        - Mix of different phonetic patterns and syllable structures
        - No proper nouns, abbreviations, or uncommon words
        
        Return ONLY this JSON format (words ONLY, no options needed):
        {{
            "words": ["word1", "word2", "word3", "word4", "word5"]
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
    

    
    