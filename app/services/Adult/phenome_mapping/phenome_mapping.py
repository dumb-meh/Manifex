import os
from openai import OpenAI
from app.services.Adult.phenome_mapping.phenome_mapping_schema import PhenomeMappingResponse
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
            word = parsed_response.get('word', '')
            options = parsed_response.get('options', [])
            
            # Generate audio for the complete word only
            audio_files = await generate_parallel_audio_files([word], "word")
            word_url = audio_files[0] if audio_files else ""           
            
            return PhenomeMappingResponse(
                word=word,
                word_url=word_url if word_url else "",
                options=options
            )
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhenomeMappingResponse(word="", word_url="", options=[])
    

        
    
    def create_prompt(self) -> str:
        prompt = """
        You are an expert language learning specialist. Create a phoneme mapping exercise to help users improve their phonemic awareness and word construction skills.
        
        Generate ONE phoneme mapping exercise consisting of:
        1. A target word (common English word, 3-6 phonemes)
        2. The word broken down into its phonetic components (correct answer)
        3. A list of phoneme options that includes the correct components plus 3-4 distractor phonemes mixed together
        
        Requirements:
        - Use a common English word (3-6 phonemes)
        - Break the word into pronounceable phoneme segments
        - Include 3-4 distractor phonemes that sound similar to the correct ones
        - Focus on commonly confused sounds (b/p, d/t, sh/ch, th/f, etc.)
        - Mix the correct phonemes with distractors in the options list
        - Make all phonemes pronounceable syllables or sounds
        
        Please return ONLY valid JSON in exactly this format:
        {
            "word": "should",
            "options": ["sh", "ch", "s", "ou", "ow", "ld", "nd"]
        }
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    