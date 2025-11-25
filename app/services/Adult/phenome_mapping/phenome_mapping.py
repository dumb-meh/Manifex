import os
from openai import OpenAI
from app.services.Adult.phenome_mapping.phenome_mapping_schema import PhenomeMappingResponse, PhenomeMappingItem
from app.utils.text_to_speech import generate_parallel_audio_files
import json


class PhenomeMapping:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    async def get_phenome_mapping(self) -> PhenomeMappingResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        try:
            parsed_response = json.loads(response)
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
            
            return PhenomeMappingResponse(exercises=exercises)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhenomeMappingResponse(exercises=[])
    

        
    
    def create_prompt(self) -> str:
        prompt = """
        You are an expert language learning specialist. Create phoneme mapping exercises to help users improve their phonemic awareness and word construction skills.
        
        Generate 5 phoneme mapping exercises. Each exercise consists of:
        1. A target word (common English word, 3-6 phonemes)
        2. A list of phoneme options that includes the correct phonetic components plus 3-4 distractor phonemes mixed together
        
        Requirements:
        - Use common English words (3-6 phonemes each)
        - Break each word into pronounceable phoneme segments
        - Include 3-4 distractor phonemes that sound similar to the correct ones for each word
        - Focus on commonly confused sounds (b/p, d/t, sh/ch, th/f, etc.)
        - Mix the correct phonemes with distractors in the options list
        - Make all phonemes pronounceable syllables or sounds
        
        Please return ONLY valid JSON in exactly this format:
        {
            "exercises": [
                {
                    "word": "should",
                    "options": ["sh", "ch", "s", "ou", "ow", "ld", "nd"]
                },
                {
                    "word": "apple", 
                    "options": ["ap", "p", "le", "b", "ple", "a", "lp"]
                },
                {
                    "word": "think",
                    "options": ["th", "f", "i", "e", "nk", "ng", "ck"]
                },
                {
                    "word": "green",
                    "options": ["gr", "br", "ee", "ea", "n", "m", "en"]
                },
                {
                    "word": "catch",
                    "options": ["c", "k", "a", "e", "tch", "ch", "sh"]
                }
            ]
        }
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    