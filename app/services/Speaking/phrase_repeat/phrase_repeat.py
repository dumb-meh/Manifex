import os
from openai import OpenAI
from app.services.Speaking.phrase_repeat.phrase_repeat_schema import PhraseRepeatRequest, PhraseRepeatResponse
import json


class PhraseRepeat:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.phrase_cache = []  # Cache for last 5 generated phrases
        
    def phrase_repeat_score(self,input:PhraseRepeatRequest, transcript) -> PhraseRepeatResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:PhraseRepeatRequest, transcript) -> str:
        prompt = f"""
        You are an expert speaking coach. Evaluate the user's pronunciation based on the following criteria: clarity, fluency, intonation, and overall effectiveness in conveying the intended message.
        you will recive the following by:
        phrase: {input.phrase}
        user transcript: {transcript}
        score each aspect on a scale of 1-10 and provide constructive feedback and suggestions for improvement
        The json response must be exactly in this format
        {{
            "score": 8,
            "feedback": "One liner feedback",
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
    
    def format_response(self, response: str) -> PhraseRepeatResponse:
        try:
            parsed_data = json.loads(response)
            return PhraseRepeatResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PhraseRepeatResponse()
        except Exception as e:
            print(f"Error creating ContextSpinResponse: {e}")
            return PhraseRepeatResponse()
        
    async def generate_phrase_repeat(self, age) -> dict:
        # Create exclusion list from cache (flatten all previous responses)
        excluded_phrases = "Good morning, All is well, Thank you, How are you, See you later"
        if self.phrase_cache:
            # Flatten all cached responses into one list
            cached_phrases = [phrase for phrases in self.phrase_cache for phrase in phrases]
            excluded_phrases += ", " + ", ".join(cached_phrases)
            
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE CREATING ANY PHRASES: {excluded_phrases}
        
        You are an expert speaking coach. Generate exactly 5 SHORT phrases for pronunciation practice based on the user's age.

        ❌ ABSOLUTE RULE: NEVER use phrases from the exclusion list above. Verify EACH phrase is completely new!
        
        STRICT REQUIREMENTS:
        - Each phrase must be 2-4 words maximum
        - Each phrase must be 8-20 characters total (including spaces)
        - Use simple, everyday greetings and common expressions
        - Focus on phrases that help with pronunciation and fluency
        - Create fresh, commonly used expressions for daily conversation

        User age: {age}

        Return ONLY a JSON object in this exact format with NO additional text:
        {{
            "phrases": ["phrase1", "phrase2", "phrase3", "phrase4", "phrase5"]
        }}

        Each phrase MUST be short and commonly used in daily conversation."""
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
            phrases = parsed_response.get('phrases', [])
            
            # Update cache with new response (keep last 5 responses)
            self.phrase_cache.append(phrases)  # Store complete phrase list
            self.phrase_cache = self.phrase_cache[-5:]  # Keep only last 5 responses
            
            return {
                "phrases": phrases
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"phrases": []}
        except Exception as e:
            print(f"Error creating phrase repeat response: {e}")
            return {"phrases": []}