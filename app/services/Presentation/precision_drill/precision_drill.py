import os
from openai import OpenAI
from app.services.Presentation.precision_drill.precision_drill_schema import PrecisionDrillRequest, PrecisionDrillResponse
import json


class PrecisionDrill:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.word_cache = []  # Cache for last 5 generated precision drills
        
    def precision_drill_score(self, input: PrecisionDrillRequest, transcript: str) -> PrecisionDrillResponse:
        prompt = self.create_prompt(input, transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: PrecisionDrillRequest, transcript: str) -> str:
        prompt = f"""You will recieve a word list and a voice transcript of user saying those words for a precision drill. Evaluate the user's performance based on clarity, speed, and accuracy in pronouncing the words. Provide a score out of 10, constructive feedback, and suggestions for improvement in JSON format.
        You will get the following by:
        Word List: {input.wordlist}
        User Transcript: {transcript}
        Now, analyze the user's performance and provide the evaluation in the following JSON format:
        {{
            "score": 8,
            "feedback": "Good clarity but needs to improve speed on certain words.", "Practice tongue twisters to enhance articulation.",
                "Focus on pacing to maintain consistent speed."
            "status": "success",
            "message": "Evaluation completed successfully."

        }}"""
        
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> PrecisionDrillResponse:
        try:
            parsed_data = json.loads(response)
            return PrecisionDrillResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PrecisionDrillResponse()
        except Exception as e:
            print(f"Error creating PrecisionDrillResponse: {e}")
            return PrecisionDrillResponse()
        
    def generate_precision_drill(self) -> dict:
        # Create exclusion list from cache (flatten all previous responses)
        excluded_words = "perception, integrity, articulate, emphasize, synergy, paradigm, ubiquitous, quintessential"
        if self.word_cache:
            # Flatten all cached drill sets
            cached_words = []
            for drill_set in self.word_cache:
                cached_words.extend(drill_set.get('slow', []))
                cached_words.extend(drill_set.get('medium', []))
                cached_words.extend(drill_set.get('fast', []))
            excluded_words += ", " + ", ".join(cached_words)
            
        prompt=f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        
        Generate a timed articulation drill with 30 words that challenge clarity and speed for adult presenters.
        
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!
        
        Words should include a mix of abstract nouns, action verbs, and tone-related adjectives. Increase difficulty gradually and provide pacing intervals (slow, medium, fast).
        
        Return ONLY a JSON object in this exact format:
        {{
            "slow": ["word1", "word2", "word3", "word4", "word5", "word6", "word7", "word8", "word9", "word10"],
            "medium": ["word11", "word12", "word13", "word14", "word15", "word16", "word17", "word18", "word19", "word20"],
            "fast": ["word21", "word22", "word23", "word24", "word25", "word26", "word27", "word28", "word29", "word30"]
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
            self.word_cache.append(parsed_response)  # Store complete drill set
            self.word_cache = self.word_cache[-5:]  # Keep only last 5 responses
            
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"slow": [], "medium": [], "fast": []}
        except Exception as e:
            print(f"Error creating precision drill response: {e}")
            return {"slow": [], "medium": [], "fast": []}