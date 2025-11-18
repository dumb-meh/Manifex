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
        
    def power_words_score(self, input: PowerWordsRequest, definition: str, sentence: str) -> PowerWordsResponse:
        prompt = self.create_prompt(input, definition, sentence)
        response = self.get_openai_response(prompt)
        return self.format_response(response)
    
    def create_prompt(self, input: PowerWordsRequest, definition: str, sentence: str) -> str:
        prompt = f"""You are an expert presentation coach. Evaluate the following word based on its impact, clarity, and relevance in presentations.

    Scoring Criteria (1-10):
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
        "score": "X/10",
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
        themes = ["Motivation", "Leadership", "Innovation", "Teamwork", "Success", "Creativity", "Growth", "Inspiration", "Change", "Resilience"]
        theme_of_the_day=random.choice(themes)
        prompt=f"“Generate a list of 10 high-impact, industry-neutral power words used frequently by presenters, educators, leaders, and broadcasters. Include short definitions and 1 example sentence for each. Change all words daily and vary by theme ({theme_of_the_day})"
        response= self.get_openai_response(prompt)
        return response