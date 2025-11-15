import os
import openai
import json
import random
from dotenv import load_dotenv
from .phoneme_flashcards_schema import PhonemeFlashcardsResponse

load_dotenv()

class PhonemeFlashcards:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Age-appropriate word lists (backup) - all 4-5 characters
        self.words_by_age = {
            "5": ["PLAY", "JUMP", "TREE", "FROG", "BIRD", "FISH", "MOON", "STAR", "BOOK", "HELP"],
            "6": ["SMILE", "HAPPY", "WATER", "GRASS", "CLOUD", "PAINT", "DANCE", "MUSIC", "HOUSE", "APPLE"],
            "7": ["PLANT", "DREAM", "BEACH", "HEART", "WORLD", "LIGHT", "SHAKE", "BREAD", "SWEET", "STORY"],
            "8": ["BRAVE", "PEACE", "CRAFT", "GRADE", "THEME", "SPACE", "SMART", "CLEAN", "PRIDE", "VOICE"]
        }

    def generate_flashcards(self, age: str) -> PhonemeFlashcardsResponse:
        """Generate a phoneme flashcard with a word and its characters and the range will be four to five character lenghth"""
        
        # Try to generate word with AI first, fallback to predefined list
        try:
            word = self._generate_word_with_ai(age)
        except:
            # Fallback to predefined words
            word_list = self.words_by_age.get(age, self.words_by_age["6"])
            word = random.choice(word_list)
        
        # Convert word to uppercase and split into characters
        word_upper = word.upper()
        characters = list(word_upper)
        
        return PhonemeFlashcardsResponse(
            word=word_upper,
            characters=characters,
            age=age
        )
    
    def _generate_word_with_ai(self, age: str) -> str:
        """Generate an age-appropriate word using OpenAI"""
        
        # Age-appropriate word length guidance - all 4-5 characters
        word_guidance = {
            "5": {"length": "4 to 5 letters", "complexity": "very simple", "examples": "play, jump, tree, bird"},
            "6": {"length": "4 to 5 letters", "complexity": "simple", "examples": "smile, happy, water, house"},
            "7": {"length": "4 to 5 letters", "complexity": "moderate", "examples": "plant, dream, beach, world"},
            "8": {"length": "4 to 5 letters", "complexity": "slightly complex", "examples": "brave, peace, craft, theme"}
        }
        
        guidance = word_guidance.get(age, word_guidance["6"])
        
        prompt = f"""Generate ONE single {guidance['complexity']} word that is appropriate for {age}-year-old children learning phonics.

Requirements:
- The word MUST be between 4 to 5 letters long (4 or 5 characters only)
- Use common, familiar words that kids know
- Examples of appropriate words: {guidance['examples']}
- The word should be easy to sound out
- Return ONLY the word in uppercase, nothing else
- No punctuation, no explanation, just ONE word
"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a phonics teacher. Generate a single word only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.8
        )
        
        word = response.choices[0].message.content.strip().upper()
        # Remove any punctuation or extra characters
        word = ''.join(c for c in word if c.isalpha())
        
        return word