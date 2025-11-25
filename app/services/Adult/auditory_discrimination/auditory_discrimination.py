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
        
        print(f"Raw OpenAI response: {response}")
        
        try:
            # Clean the response - remove any markdown code blocks or extra formatting
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            parsed_response = json.loads(cleaned_response)
            word_pairs_raw = parsed_response.get('word_pairs', [])
            
            # Extract word pairs and answers for flat format
            word_pairs = []
            answers = []
            
            for pair_data in word_pairs_raw:
                word_pair = {
                    "word1": pair_data.get('word1', ''),
                    "word2": pair_data.get('word2', ''),
                    "answer": pair_data.get('answer', '')
                }
                word_pairs.append(word_pair)
            
            print(f"Extracted word_pairs: {word_pairs}")
            
            if not word_pairs:
                print("Warning: Empty word_pairs detected")
                return {"word_pairs": []}
            
            # Generate audio using the original optimized method
            enriched_word_pairs = await self.generate_optimized_audio(word_pairs)
            
            return {
                "word_pairs": enriched_word_pairs
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response was: {response}")
            return {"word_pairs": [], "answers": []}
        except Exception as e:
            print(f"Unexpected error: {e}")
            print(f"Raw response was: {response}")
            return {"word_pairs": [], "answers": []}
    
    async def generate_optimized_audio(self, word_pairs: list) -> list:
        """
        Generate audio files optimally - only generate once for same words, twice for different words
        """
        texts_to_convert = []
        text_mapping = {} 
        enriched_word_pairs = []
        
        for i, pair in enumerate(word_pairs):
            word1 = pair.get('word1', '')
            word2 = pair.get('word2', '')
            answer = pair.get('answer', '')
            
            if answer.lower() == "same" or word1 == word2:
                if word1 not in text_mapping:
                    text_mapping[word1] = len(texts_to_convert)
                    texts_to_convert.append(word1)
                
                enriched_pair = {
                    "word1": word1,
                    "word2": word2,
                    "answer": answer,
                    "audio_file1": None,  
                    "audio_file2": None   
                }
            else:
                if word1 not in text_mapping:
                    text_mapping[word1] = len(texts_to_convert)
                    texts_to_convert.append(word1)
                
                if word2 not in text_mapping:
                    text_mapping[word2] = len(texts_to_convert)
                    texts_to_convert.append(word2)
                
                enriched_pair = {
                    "word1": word1,
                    "word2": word2,
                    "answer": answer,
                    "audio_file1": None,  
                    "audio_file2": None   
                }
            
            enriched_word_pairs.append(enriched_pair)
        
        audio_files = await generate_parallel_audio_files(texts_to_convert, "word_pair")
        
        text_to_audio = {}
        for text, audio_file in zip(texts_to_convert, audio_files):
            if audio_file: 
                text_to_audio[text] = audio_file
        
        for i, pair in enumerate(word_pairs):
            word1 = pair.get('word1', '')
            word2 = pair.get('word2', '')
            answer = pair.get('answer', '')
            
            enriched_word_pairs[i]["audio_file1"] = text_to_audio.get(word1)
            
            if answer.lower() == "same" or word1 == word2:
                enriched_word_pairs[i]["audio_file2"] = text_to_audio.get(word1)
            else:
                enriched_word_pairs[i]["audio_file2"] = text_to_audio.get(word2)
        
        return enriched_word_pairs
    
    async def generate_optimized_audio_for_lists(self, word_pairs_lists: list) -> list:
        """
        Generate audio files for the list of dictionaries format
        Each word_pair_list contains [{"word": "word1", "answer": "same"}, {"word": "word2", "answer": "same"}]
        """
        unique_words = set()
        for word_pair_list in word_pairs_lists:
            for word_dict in word_pair_list:
                unique_words.add(word_dict.get('word', ''))
        
        words_to_convert = list(unique_words)
        print(f"Generating audio for {len(words_to_convert)} unique words: {words_to_convert}")
        
        audio_files = await generate_parallel_audio_files(words_to_convert, "word_pair")
        
        word_to_audio = {}
        for word, audio_file in zip(words_to_convert, audio_files):
            if audio_file:
                word_to_audio[word] = audio_file
                
        enriched_word_pairs = []
        for word_pair_list in word_pairs_lists:
            enriched_pair_list = []
            for word_dict in word_pair_list:
                word = word_dict.get('word', '')
                answer = word_dict.get('answer', '')
                
                enriched_dict = {
                    "word": word,
                    "answer": answer,
                    "audio_file": word_to_audio.get(word)
                }
                enriched_pair_list.append(enriched_dict)
            
            enriched_word_pairs.append(enriched_pair_list)
        
        return enriched_word_pairs
        
    
    def create_prompt(self) -> str:
        prompt = """
        You are an expert language learning specialist creating auditory discrimination exercises. Generate high-quality word pairs for pronunciation practice.
        
        Requirements:
        - Generate exactly 5 word pairs
        - Use meaningful, common English words (NOT function words like "to", "a", "the")
        - Include some paris that are identical (same word twice), (it may be 0 to 2 pairs)
        - Include some pairs that are similar-sounding but different (it may be 0 to 3 pairs)
        - Focus on minimal pairs that differ by one sound (ship/sheep, pen/pin, etc.)
        - Use words that are at least 3 letters long
        - Avoid proper nouns, abbreviations, or uncommon words
        
        Good examples of different pairs:
        - ship/sheep (i/ee sound difference)
        - pen/pin (e/i vowel difference)  
        - cat/cut (a/u vowel difference)
        - bear/beer (ar/eer ending difference)
        - thick/sick (th/s consonant difference)
        
        Please return ONLY valid JSON in exactly this format:
        {
            "word_pairs": [
                {"word1": "ship", "word2": "ship","answer": "same"},
                {"word1": "pen", "word2": "pin","answer": "different"},
                {"word1": "cat", "word2": "cut","answer": "different"},
                {"word1": "bear", "word2": "beer","answer": "different"},
                {"word1": "thick", "word2": "thick","answer": "same"}
          ]
        }
        
        Ensure the answers array correctly indicates "same" or "different" for each pair.
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
        
    