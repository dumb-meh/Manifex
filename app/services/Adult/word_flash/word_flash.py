import os
from openai import OpenAI
from app.services.Adult.word_flash.word_flash_schema import WordFlashRequest, WordFlashResponse
import json
import re


class WordFlash:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.word_cache = []  # Store last 5 words
        
    def word_flash_score(self,input:WordFlashRequest, transcript) -> WordFlashResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:WordFlashRequest, transcript) -> str:
        prompt = f"""
        You are an expert speaking practice coach.
        You will receive the following:
        word: {input.word}
        user transcript: {transcript}

        CRITICAL: IMMEDIATE REJECTION RULES - CHECK THESE FIRST BEFORE SCORING:
        - If transcript is empty, whitespace, silence-like, or missing, RETURN score = 0 immediately.
        - This is a single-word speaking task, so one word is expected.
        - If the spoken word does not match or clearly attempt the target word, RETURN score = 0 immediately.
        - If transcript is filler/repetitive/nonsensical/unrelated to the target word, RETURN score = 0 immediately.
        - If transcript is just a random common word (e.g., "you", "hello", "test") and not the target, RETURN score = 0 immediately.

        STRICT SCORING RULES (apply only if not rejected above):
        1) Be very strict. Never reward vague, partial, or generic responses.
        2) Never assume meaning that is not clearly present in the transcript.
        3) Evaluate pronunciation accuracy, clarity, and confidence of the target word.
        4) If pronunciation is weak/unclear or only partly correct, score must be below 40.
        5) If pronunciation is understandable but not clean, score must stay between 40 and 69.
        6) Give 70-84 only when pronunciation is clear and mostly accurate.
        7) Give 85-100 only for highly accurate, clear, and confident pronunciation.
        8) Penalize mispronunciation, hesitation, and non-target word usage.

        Provide constructive feedback and suggestions for improvement.
        Keep feedback concise and vary the phrasing across requests to avoid repetition.

        The JSON response must be exactly in this format:
        {{
            "score": 8,
            "feedback": "Great pronunciation; try to improve clarity",
            "status": "success",
            "message": "Evaluation completed successfully."

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
    

    
    def format_response(self, response: str) -> WordFlashResponse:
        try:
            # Simple JSON cleaning
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            parsed_data = json.loads(cleaned)
            return WordFlashResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return WordFlashResponse()
        except Exception as e:
            print(f"Error creating WordFlashResponse: {e}")
            return WordFlashResponse()
        
    def generate_word_flash(self) -> dict:
        # Create exclusion list from cache (flatten all previous responses)
        excluded_words = ""
        if self.word_cache:
            # Flatten all cached responses into one list
            cached_words = [word for response in self.word_cache for word in response]
            excluded_words = f"⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {', '.join(cached_words)}\n\n❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!\n\n"
        
        prompt = f"""You are expert speaking coach. In order to improve speaking skills, you will provide a list of 5 challenging words.
        
        {excluded_words}Return ONLY a JSON object in this exact format:
        {{
            "words": ["word1", "word2", "word3", "word4", "word5"]
        }}
        
        Do not include any additional text or formatting."""
        response = self.get_openai_response(prompt)
        try:
            # Simple JSON cleaning
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            parsed_response = json.loads(cleaned)
            words = parsed_response.get('words', [])
            
            # Update cache with new response (keep last 5 responses)
            self.word_cache.append(words)  # Store complete response
            self.word_cache = self.word_cache[-5:]  # Keep only last 5 responses
            
            return {
                "words": words
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"words": []}