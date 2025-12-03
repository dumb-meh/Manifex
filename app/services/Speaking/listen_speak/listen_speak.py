import os
from openai import OpenAI
from app.services.Speaking.listen_speak.listen_speak_schema import ListenSpeakRequest, ListenSpeakResponse
import json


class ListenSpeak:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.sentence_cache = []  # Cache for last 5 generated sentences
        
    def listen_speak_score(self,input:ListenSpeakRequest, transcript) -> ListenSpeakResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:ListenSpeakRequest, transcript) -> str:
        prompt = f"""
        You are an expert speaking practice coach.
        you will recive the following by:
        senetence: {input.sentence}
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
    
    def format_response(self, response: str) -> ListenSpeakResponse:
        try:
            parsed_data = json.loads(response)
            return ListenSpeakResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return ListenSpeakResponse()
        except Exception as e:
            print(f"Error creating ListenSpeakResponse: {e}")
            return ListenSpeakResponse()
        
    async def generate_listen_speak(self, age) -> dict:
        age_int = int(age)
        
        # Define age-appropriate sentence guidelines
        if age_int < 8:
            sentence_guide = {
                "length": "3-5 words maximum",
                "complexity": "very simple",
                "examples": "I like cats, The sun is hot, My dog runs fast, Birds can fly, I eat apples"
            }
        elif age_int < 12:
            sentence_guide = {
                "length": "5-8 words maximum", 
                "complexity": "simple",
                "examples": "The happy cat sleeps on the bed, I want to play outside today, My favorite color is bright blue"
            }
        elif age_int < 16:
            sentence_guide = {
                "length": "8-12 words maximum",
                "complexity": "moderate", 
                "examples": "The children played games in the park after school, I really enjoy reading interesting books on weekends"
            }
        else:
            sentence_guide = {
                "length": "10-15 words maximum",
                "complexity": "challenging but reasonable",
                "examples": "The talented musician practiced diligently every day to improve their performance skills significantly"
            }
        
        # Create exclusion list from cache (flatten all previous responses)
        excluded_sentences = "I like cats, The sun is hot, My dog runs fast, Birds can fly"
        if self.sentence_cache:
            # Flatten all cached responses into one list
            cached_sentences = [sentence for sentences in self.sentence_cache for sentence in sentences]
            excluded_sentences += ", " + ", ".join(cached_sentences)
        
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE CREATING ANY SENTENCES: {excluded_sentences}
        
        You are an expert speaking coach. Generate 5 age-appropriate sentences for a {age}-year-old child to practice speaking.

        ❌ ABSOLUTE RULE: NEVER use sentences from the exclusion list above. Verify EACH sentence is completely new!
        
        STRICT REQUIREMENTS FOR AGE {age}:
        - Each sentence must be {sentence_guide['length']}
        - Use {sentence_guide['complexity']} vocabulary appropriate for age {age}
        - Focus on clear pronunciation practice, not tongue twisters
        - Use familiar topics: family, animals, food, school, play, colors, etc.
        - Examples: {sentence_guide['examples']}

        AVOID:
        - Tongue twisters or overly complex phrases
        - Advanced vocabulary beyond the child's age level
        - Sentences longer than the specified word count
        - Repetitive alliterative phrases

        Return ONLY a JSON object in this exact format:
        {{
            "sentences": ["sentence1", "sentence2", "sentence3", "sentence4", "sentence5"]
        }}

        Make sure each sentence is appropriate for a {age}-year-old's speaking ability."""
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
            sentences = parsed_response.get('sentences', [])
            
            # Update cache with new response (keep last 5 responses)
            self.sentence_cache.append(sentences)  # Store complete sentence list
            self.sentence_cache = self.sentence_cache[-5:]  # Keep only last 5 responses
            
            return {
                "sentences": sentences
            }
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"sentences": []}
        except Exception as e:
            print(f"Error creating listen speak response: {e}")
            return {"sentences": []}