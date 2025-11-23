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
            phenome_data_answers = parsed_response.get('phenome_data_answers', [])
            phenome_data_options = parsed_response.get('phenome_data_options', [])
            
            enriched_answers, enriched_options = await self.generate_audio_for_all_syllables(
                phenome_data_answers, phenome_data_options
            )
            
            return {
                "phenome_data_answers": enriched_answers,
                "phenome_data_options": enriched_options
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"phenome_data_answers": [], "phenome_data_options": []}
    
    async def generate_audio_for_all_syllables(self, phenome_data_answers: list, phenome_data_options: list) -> tuple[list, list]:
        """
        Generate audio files for all unique syllables across both answers and options.
        Returns enriched answers and options with audio URLs for each syllable.
        """
        unique_syllables = set()
        
        for answer_set in phenome_data_answers:
            unique_syllables.update(answer_set)
        
        for option_set in phenome_data_options:
            unique_syllables.update(option_set)
        
        syllables_to_convert = list(unique_syllables)
        
        print(f"Generating audio for {len(syllables_to_convert)} unique syllables: {syllables_to_convert}")

        audio_files = await generate_parallel_audio_files(syllables_to_convert, "syllable")
        
        syllable_to_audio = {}
        for syllable, audio_file in zip(syllables_to_convert, audio_files):
            if audio_file:  
                syllable_to_audio[syllable] = audio_file
        
        enriched_answers = []
        for answer_set in phenome_data_answers:
            enriched_answer_set = []
            for syllable in answer_set:
                enriched_syllable = {
                    "syllable": syllable,
                    "audio_file": syllable_to_audio.get(syllable)
                }
                enriched_answer_set.append(enriched_syllable)
            enriched_answers.append(enriched_answer_set)
        
        enriched_options = []
        for option_set in phenome_data_options:
            enriched_option_set = []
            for syllable in option_set:
                enriched_syllable = {
                    "syllable": syllable,
                    "audio_file": syllable_to_audio.get(syllable)
                }
                enriched_option_set.append(enriched_syllable)
            enriched_options.append(enriched_option_set)
        
        return enriched_answers, enriched_options
        
    
    def create_prompt(self) -> str:
        prompt = """
        You are an expert language learning specialist. Create phoneme mapping exercises to help users improve their phonemic awareness and word construction skills.
        
        Generate 5 phoneme mapping exercises. Each exercise consists of:
        1. A target word broken down into its phonetic components (answer)
        2. A set of phonetic options that includes the correct components plus distractors
        
        Requirements:
        - Use common English words (3-6 phonemes each)
        - Include 2-3 distractor phonemes for each word
        - Focus on commonly confused sounds (b/p, d/t, sh/ch, th/f, etc.)
        - Make phonemes pronounceable syllables or sounds
        
        Please return ONLY valid JSON in exactly this format:
        {
            "phenome_data_answers": [
                ["sh", "ou", "ld"],
                ["b", "a", "t"],
                ["th", "i", "nk"],
                ["f", "i", "sh"],
                ["c", "a", "t"]
            ],
            "phenome_data_options": [
                ["sh", "ch", "s", "ou", "ow", "ld", "nd"],
                ["b", "p", "a", "e", "t", "d"],
                ["th", "f", "i", "e", "nk", "ng", "ck"],
                ["f", "v", "i", "e", "sh", "ch", "s"],
                ["c", "k", "a", "e", "t", "d"]
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
    