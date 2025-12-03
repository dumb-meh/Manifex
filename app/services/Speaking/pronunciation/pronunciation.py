import os
from openai import OpenAI
from app.services.Speaking.pronunciation.pronunciation_schema import PronunciationRequest, PronunciationResponse
import json


class Pronunciation:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.word_cache = []  # Cache for last 5 generated pronunciation words
        
    def pronunciation_score(self,input:PronunciationRequest, transcript) -> PronunciationResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:PronunciationRequest, transcript) -> str:
        prompt = f"""
        You are an expert speaking practice coach.
        you will recive the following by:
        word: {input.word}
        user transcript: {transcript}
        score each aspect on a scale of 1-10 and provide constructive feedback and suggestions for improvement
        The json response must be exactly in this format
        {{
            "score": 8,
            "feedback": "One liner feedback such as "great pronunciation","try better next time",
            "status": "success",
            "message": "Evaluation completed successfully."

        }}
        
        """  
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> PronunciationResponse:
        try:
            parsed_data = json.loads(response)
            return PronunciationResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PronunciationResponse()
        except Exception as e:
            print(f"Error creating PronunciationResponse: {e}")
            return PronunciationResponse()
        
    async def generate_pronunciation(self, age) -> dict:
        # Create exclusion list from cache (flatten all previous responses)
        excluded_words = "pronunciation, articulation, vocabulary, communication, fluency"
        if self.word_cache:
            # Flatten all cached responses into one list
            cached_words = [word for words in self.word_cache for word in words]
            excluded_words += ", " + ", ".join(cached_words)
            
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        
        You are expert speaking coach. In order to improve speaking skills, you will provide a list of 5 challenging words based on their age.
        
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!
        
        User age is {age}. Select age-appropriate pronunciation challenges.
        
        Return ONLY a JSON object in this exact format:
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
            self.word_cache.append(words)  # Store complete word list
            self.word_cache = self.word_cache[-5:]  # Keep only last 5 responses
            
            return {
                "words": words
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"words": []}
        except Exception as e:
            print(f"Error creating pronunciation response: {e}")
            return {"words": []}