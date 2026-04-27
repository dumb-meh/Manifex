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
        print(f"[FlowChain] scoring called with transcript: '{transcript}' and word_list: {input.word_list}")
        prompt = self.create_prompt(input,transcript)
        print(f"[FlowChain] prompt sent to OpenAI:\n{prompt}")
        response = self.get_openai_response(prompt)
        print(f"[FlowChain] raw OpenAI response: {response}")
        return self.format_response(response)
    
    def create_prompt(self, input: FlowChainRequest,transcript) -> str:
        prompt = f"""You are an expert presentation coach. Evaluate the following connected words based on flow, relevance, correctness, and contextual usage.

        ⚠️ CRITICAL: IMMEDIATE REJECTION RULES - CHECK THESE FIRST BEFORE SCORING:
        - If transcript is empty, single word, or less than 5 words total, RETURN SCORE = 0 IMMEDIATELY.
        - If transcript contains only pronouns or articles (e.g., "you", "the", "a"), RETURN SCORE = 0 IMMEDIATELY.
        - If fewer than 3 of the target words appear in the transcript, RETURN SCORE = 0 IMMEDIATELY.
        - Single-word or one-two word responses are ALWAYS 0 — no exceptions.

        STRICT SCORING RULES (apply ONLY if not rejected above):
        1) Be extremely harsh. Never reward vague, incomplete, generic, or partially correct responses.
        2) Never assume meaning that is not explicitly present in the user's transcript.
        3) If most target words are missing or misused, score must be below 40.
        4) If response is average but incomplete, score must be between 40-69.
        5) Give 70-84 only when most words are used correctly with clear, logical flow.
        6) Give 85-100 only when usage is precise, natural, coherent, and demonstrates strong mastery across the chain.
        7) Always penalize grammar errors, word-order breakdown, forced phrasing, and off-topic content.

        Connected words: {input.word_list}
        User pronounced words: {transcript}

        Score based on how many words were used correctly in context on a scale of 0-100, and provide constructive feedback and suggestions for improvement.

        The JSON response must be exactly in this format:
        {{
            "score": 86,
            "feedback": "",
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