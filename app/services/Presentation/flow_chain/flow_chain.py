import os
from openai import OpenAI
from app.services.Presentation.flow_chain.flow_chain_schema import FlowChainRequest, FlowChainResponse
import json


class FlowChain:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def flow_chain_score(self, input: FlowChainRequest,transcript) -> FlowChainResponse:
        prompt = self.create_prompt(input)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: FlowChainRequest,transcript) -> str:
        prompt = f"""you are an expert presentation coach. Evaluate the following connected words based on their flow and relevance.
        connected words: {input.word_list}
        transcript: {transcript}
        score each aspect on a scale of 1-10 and provide constructive feedback and suggestions for improvement
        The json response must be exactly in this format
        {{
            "score": 8,
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
    
    def format_response(self, response: str) -> FlowChainRequest:
        try:
            parsed_data = json.loads(response)
            return FlowChainResponse(**parsed_data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return FlowChainRequest()
        except Exception as e:
            print(f"Error creating FlowChainResponse: {e}")
            return FlowChainResponse()
    
    def generate_flow_chain(self) -> list:
        prompt = f"""Create 10 connected words (e.g., vision → action → growth → impact → legacy) to enhance fluency and neural speed by chaining related vocabulary into cohesive micro-speeches.
         return a json in the following format:
        {{
            "words": [word1, word2, word3, word4, word5, word6, word7, word8, word9, word10]
        }}
        """
        response = self.get_openai_response(prompt)
        return self.format_response(response)