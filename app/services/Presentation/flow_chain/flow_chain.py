import os
from openai import OpenAI
from app.services.Presentation.flow_chain.flow_chain_schema import FlowChainRequest, FlowChainResponse
import json


class FlowChain:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        self.word_cache = []  # Cache for last 5 generated word chains
        
    def flow_chain_score(self, input: FlowChainRequest,transcript) -> FlowChainResponse:
        prompt = self.create_prompt(input,transcript)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: FlowChainRequest,transcript) -> str:
        prompt = f"""you are an expert presentation coach. Evaluate the following connected words based on their flow and relevance.
        connected words: {input.word_list}
        user pronounced words: {transcript}
        score it based on how many wors were used correctly in context on a scale of 0-100 and provide constructive feedback and suggestions for improvement.
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
    
    def format_response(self, response: str) -> FlowChainResponse:
        try:
            parsed_data = json.loads(response)
            return FlowChainResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return FlowChainResponse()
        except Exception as e:
            print(f"Error creating FlowChainResponse: {e}")
            return FlowChainResponse()
    
    def generate_flow_chain(self) -> list:
        # Create exclusion list from cache (flatten all previous responses)
        excluded_words = "vision, action, growth, impact, legacy, success, innovation, leadership"
        if self.word_cache:
            # Flatten all cached word chains
            cached_words = [word for word_chain in self.word_cache for word in word_chain]
            excluded_words += ", " + ", ".join(cached_words)
            
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        
        Create 10 connected words to enhance fluency and neural speed by chaining related vocabulary into cohesive micro-speeches.
        
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!
        
        Create a logical flow where each word connects meaningfully to the next (e.g., vision → strategy → execution → results → celebration).
        
        Return ONLY a JSON object in this exact format:
        {{
            "words": ["word1", "word2", "word3", "word4", "word5", "word6", "word7", "word8", "word9", "word10"]
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
            word_chain = parsed_response.get("words", [])
            
            # Update cache with new response (keep last 5 responses)
            self.word_cache.append(word_chain)  # Store complete word chain
            self.word_cache = self.word_cache[-5:]  # Keep only last 5 responses
            
            return word_chain
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return []
        except Exception as e:
            print(f"Error creating flow chain response: {e}")
            return []