import os
from openai import OpenAI
from app.services.Presentation.context_spin.context_spin_schema import ContextSpinRequest, ContextSpinResponse
import json


class ContextSpin:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.content_cache = []  # Cache for last 5 generated content
        
    def context_spin_score(self,input:ContextSpinRequest, transcript) -> ContextSpinResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input:ContextSpinRequest, transcript) -> str:
        prompt = f"""
        You are an expert presentation coach. Evaluate the following text based on its context relevance and vocabulary integration.
        you will recive the following by:
        scenario: {input.scenario}
        user transcript: {transcript}
        score each aspect on a scale of 0-100 and provide constructive feedback and suggestions for improvement
        The json response must be exactly in this format
        {{
            "score": 86,
            "feedback": ""
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
    
    def format_response(self, response: str) -> ContextSpinResponse:
        try:
            parsed_data = json.loads(response)
            return ContextSpinResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return ContextSpinResponse()
        except Exception as e:
            print(f"Error creating ContextSpinResponse: {e}")
            return ContextSpinResponse()
        
    def generate_context_spin(self) -> dict:
        # Create exclusion list from cache (flatten all previous responses)
        excluded_words = "motivation, leadership, innovation, success"
        excluded_scenarios = "wedding reception, press conference, TED talk, team meeting"
        if self.content_cache:
            # Flatten all cached responses
            cached_words = [word for response in self.content_cache for word in response.get('words', [])]
            cached_scenarios = [response.get('scenario', '') for response in self.content_cache if response.get('scenario')]
            
            if cached_words:
                excluded_words += ", " + ", ".join(cached_words)
            if cached_scenarios:
                excluded_scenarios += ", " + ", ".join(cached_scenarios)
                
        prompt = f"""⚠️ FIRST: CHECK THESE EXCLUSION LISTS BEFORE SELECTING ANY CONTENT:
        EXCLUDED WORDS: {excluded_words}
        EXCLUDED SCENARIOS: {excluded_scenarios}
        
        You are expert presentation coach. In order to improve spontaneous verbal thinking and vocabulary integration.
        
        ❌ ABSOLUTE RULE: NEVER use words or scenarios from the exclusion lists above. Verify EACH item is completely new!
        
        Give 5 key vocabulary words and 1 random scenario for presentation practice.
        
        Return ONLY a JSON object in this exact format:
        {{
            "words": ["word1", "word2", "word3", "word4", "word5"],
            "scenario": "suppose you are speaking at [new scenario]"
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
            
            # Update cache with new response (keep last 5 responses)
            self.content_cache.append(parsed_response)  # Store complete response
            self.content_cache = self.content_cache[-5:]  # Keep only last 5 responses
            
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"words": [], "scenario": ""}
        except Exception as e:
            print(f"Error creating context spin response: {e}")
            return {"words": [], "scenario": ""}