import os
from openai import OpenAI
from app.services.Presentation.power_words.power_words_schema import PowerWordsRequest, PowerWordsResponse
import json
import random


class PowerWords:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.word_cache = []  # Cache for last 5 generated power words
        
    def power_words_score(self, input: PowerWordsRequest, definition: str, sentence: str) -> PowerWordsResponse:
        prompt = self.create_prompt(input, definition, sentence)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: PowerWordsRequest, definition: str, sentence: str) -> str:
        prompt = f"""You are an expert presentation coach. Evaluate the following word based on its impact, clarity, and relevance in presentations.

    Scoring Criteria (0-100):
    - Impact: How powerful and memorable is this word?
    - Clarity: How well does the user understand and use the word?
    - Relevance: How suitable is this word for presentations?

    Details to evaluate:
    Word: {input.word}
    User's Definition: {definition}
    User's Example Sentence: {sentence}

    Provide constructive feedback and suggestions for improvement.

    Respond in the following JSON format:
    {{
        "score": 56,
        "feedback": "Constructive feedback and suggestions for improvement",
        "status": "success",
        "message": "Brief summary of the evaluation"
    }}
    """
        return prompt
    
    def get_openai_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[ {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def format_response(self, response: str) -> PowerWordsResponse:
        try:
            parsed_data = json.loads(response)
            return PowerWordsResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return PowerWordsResponse()
        except Exception as e:
            print(f"Error creating PowerWordsResponse: {e}")
            return PowerWordsResponse()
    
    
    def generate_power_words(self) -> list:
        # Create exclusion list from cache (flatten all previous responses)
        excluded_words = "motivation, leadership, innovation, teamwork, success, creativity, growth, inspiration"
        if self.word_cache:
            # Flatten all cached word lists
            cached_words = [word for word_list in self.word_cache for word in word_list]
            excluded_words += ", " + ", ".join(cached_words)
            
        themes = ["Motivation", "Leadership", "Innovation", "Teamwork", "Success", "Creativity", "Growth", "Inspiration", "Change", "Resilience"]
        theme_of_the_day=random.choice(themes)
        
        prompt=f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        
        Generate a list of 10 high-impact, industry-neutral power words used frequently by presenters, educators, leaders, and broadcasters.
        
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!
        
        Focus on the theme: {theme_of_the_day}
        
        Return ONLY a JSON object in this exact format:
        {{"words": ["word1", "word2", "word3", "word4", "word5", "word6", "word7", "word8", "word9", "word10"]}}
        
        Do not include definitions or example sentences. Only return the word strings in the array."""
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
            word_list = parsed_response.get("words", [])
            
            # Update cache with new response (keep last 5 responses)
            self.word_cache.append(word_list)  # Store complete word list
            self.word_cache = self.word_cache[-5:]  # Keep only last 5 responses
            
            return word_list
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return []
        except Exception as e:
            print(f"Error creating power words response: {e}")
            return []