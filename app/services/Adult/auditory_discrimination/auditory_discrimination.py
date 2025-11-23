import os
from openai import OpenAI
from app.services.Adult.auditory_discrimination.auditory_discrimination_schema import AuditoryDiscriminationResponse
from app.utils.text_to_speech import generate_parallel_audio_files
import json


class AuditoryDiscrimination:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    async def get_auditory_discrimination(self) -> AuditoryDiscriminationResponse:
        prompt = self.create_prompt()
        response = self.get_openai_response(prompt)
        try:
            parsed_response = json.loads(response)
            word_pairs = parsed_response.get('word_pairs', [])
            answers = parsed_response.get('answers', [])
            
            # Create optimized audio generation based on word pairs and answers
            enriched_word_pairs = await self.generate_optimized_audio(word_pairs, answers)
            
            return {
                "word_pairs": enriched_word_pairs,
                "answers": answers
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"word_pairs": [], "answers": []}
    
    async def generate_optimized_audio(self, word_pairs: list, answers: list) -> list:
        """
        Generate audio files optimally - only generate once for same words, twice for different words
        """
        # Create a list of unique texts to convert and track their mapping
        texts_to_convert = []
        text_mapping = {}  # Maps index in texts_to_convert to audio file path
        enriched_word_pairs = []
        
        for i, (pair, answer) in enumerate(zip(word_pairs, answers)):
            word1 = pair.get('word1', '')
            word2 = pair.get('word2', '')
            
            if answer.lower() == "same" or word1 == word2:
                # Same words - generate audio only once
                if word1 not in text_mapping:
                    text_mapping[word1] = len(texts_to_convert)
                    texts_to_convert.append(word1)
                
                enriched_pair = {
                    "word1": word1,
                    "word2": word2,
                    "audio_file1": None,  # Will be filled after audio generation
                    "audio_file2": None   # Will be same as audio_file1
                }
            else:
                # Different words - generate audio for both
                if word1 not in text_mapping:
                    text_mapping[word1] = len(texts_to_convert)
                    texts_to_convert.append(word1)
                
                if word2 not in text_mapping:
                    text_mapping[word2] = len(texts_to_convert)
                    texts_to_convert.append(word2)
                
                enriched_pair = {
                    "word1": word1,
                    "word2": word2,
                    "audio_file1": None,  # Will be filled after audio generation
                    "audio_file2": None   # Will be filled after audio generation
                }
            
            enriched_word_pairs.append(enriched_pair)
        
        # Generate TTS audio files for unique texts only
        audio_files = await generate_parallel_audio_files(texts_to_convert, "word_pair")
        
        # Create a mapping from text to audio file path
        text_to_audio = {}
        for text, audio_file in zip(texts_to_convert, audio_files):
            if audio_file:  # Only map if audio generation was successful
                text_to_audio[text] = audio_file
        
        # Fill in the audio file paths in enriched_word_pairs
        for i, (pair, answer) in enumerate(zip(word_pairs, answers)):
            word1 = pair.get('word1', '')
            word2 = pair.get('word2', '')
            
            enriched_word_pairs[i]["audio_file1"] = text_to_audio.get(word1)
            
            if answer.lower() == "same" or word1 == word2:
                # Use the same audio file for both words
                enriched_word_pairs[i]["audio_file2"] = text_to_audio.get(word1)
            else:
                # Use different audio files
                enriched_word_pairs[i]["audio_file2"] = text_to_audio.get(word2)
        
        return enriched_word_pairs
        
    
    def create_prompt(self) -> str:
        prompt = """
        You are an expert speaking language learning expert. Your job is to create auditory discrimination exercises to help users improve their listening skills.
        Generate 5 pairs of similar-sounding words that are commonly confused in English. Some pairs should be the same word written twice, others should be different similar-sounding words.
        
        Please return ONLY valid JSON in exactly this format:
        {
            "word_pairs": [
                {"word1": "bat", "word2": "bat"},
                {"word1": "ship", "word2": "sheep"},
                {"word1": "cat", "word2": "cut"},
                {"word1": "pen", "word2": "pin"},
                {"word1": "full", "word2": "fool"}
            ],
            "answers": ["same", "different", "different", "different", "different"]
        }
        
        Make sure the answers array corresponds to whether each word pair is "same" or "different".
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> AuditoryDiscriminationResponse:
        try:
            parsed_data = json.loads(response)
            return AuditoryDiscriminationResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return AuditoryDiscriminationResponse()
        except Exception as e:
            print(f"Error creating AuditoryDiscriminationResponse: {e}")
            return AuditoryDiscriminationResponse()
        
    