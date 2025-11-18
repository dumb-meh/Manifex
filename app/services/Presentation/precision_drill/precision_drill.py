import os
from openai import OpenAI
from app.services.Presentation.precision_drill.precision_drill_schema import PrecisionDrillRequest, PrecisionDrillResponse
import json


class PrecisionDrill:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        
    def precision_drill(self, input: PrecisionDrillRequest) -> PrecisionDrillResponse:
        prompt = self.create_prompt(input)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: PrecisionDrillRequest, transcript: str) -> str:
        prompt = f"""You will recieve a word list and a voice transcript of user saying those words for a precision drill. Evaluate the user's performance based on clarity, speed, and accuracy in pronouncing the words. Provide a score out of 10, constructive feedback, and suggestions for improvement in JSON format.
        You will get the following by:
        Word List: {input.wordlist}
        User Transcript: {transcript}"""
        
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
    def get_precision_drill(self) -> list:
        prompt=f"""Generate a timed articulation drill with 40 words that challenge clarity and speed for adult presenters. Words should include a mix of abstract nouns, action verbs, and tone-related adjectives. Increase difficulty gradually and ensure a new set of words daily. Provide pacing intervals (slow, medium, fast)
        Response in JSON format as:
        {{
            "slow": [perception, integrity, articulate, emphasize, collaborate, innovate, resonate, dynamic, empathy, clarity],
            "medium": [synergy, paradigm, leverage, holistic, proactive, transformative, agile, scalable, disruptive, visionary],
            "fast": [ubiquitous, quintessential, conundrum, serendipity, dichotomy, ubiquitous, quintessential, conundrum, serendipity, dichotomy]    ...
            
        }}"""
        response = self.get_openai_response(prompt)
        return response