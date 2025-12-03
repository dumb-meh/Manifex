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
        self.word_cache = []  # Cache for last 5 generated words
        
        # Age-appropriate word lists (backup) - organized by word length
        self.words_by_age = {
            # Ages < 8: 3-letter words
            "3": ["CAT", "DOG", "SUN", "BOX", "HAT", "PEN", "CUP", "BED", "RED", "TOP"],
            "4": ["CAR", "BAT", "RUN", "FUN", "BIG", "HOT", "NET", "MOM", "DAD", "BUS"],
            "5": ["BAG", "EGG", "LOG", "HUG", "WIN", "ZIP", "JOB", "MAP", "PIG", "TOY"],
            "6": ["BUG", "WET", "DIG", "SIT", "HIT", "CUT", "PUT", "GET", "LET", "SET"],
            "7": ["FIX", "MIX", "SIX", "BOW", "COW", "NOW", "LAP", "NAP", "TAP", "RAP"],
            # Ages 8-14: 4-letter words
            "8": ["PLAY", "JUMP", "TREE", "FROG", "BIRD", "FISH", "MOON", "STAR", "BOOK", "HELP"],
            "9": ["WALK", "TALK", "GAME", "NAME", "TIME", "LINE", "BLUE", "MAKE", "TAKE", "LIKE"],
            "10": ["HOLD", "TOLD", "COLD", "GOLD", "HAND", "LAND", "SEND", "BEND", "MIND", "KIND"],
            "11": ["WIND", "FIND", "WILD", "MILD", "WORD", "WORK", "PARK", "DARK", "MARK", "BARK"],
            "12": ["FILM", "MILK", "SILK", "BULK", "HELP", "KELP", "MELT", "BELT", "FELT", "WELT"],
            "13": ["SWIM", "SLIM", "TRIM", "GRIM", "DRUM", "PLUM", "GLUM", "HUMP", "JUMP", "PUMP"],
            "14": ["CAMP", "LAMP", "DAMP", "RAMP", "BUMP", "LUMP", "DUMP", "TEMP", "HEMP", "WIMP"],
            # Ages >= 15: 5-letter words
            "15": ["PLANT", "DREAM", "BEACH", "HEART", "WORLD", "LIGHT", "SHAKE", "BREAD", "SWEET", "STORY"],
            "16": ["BRAVE", "PEACE", "CRAFT", "GRADE", "THEME", "SPACE", "SMART", "CLEAN", "PRIDE", "VOICE"],
            "17": ["SMILE", "HAPPY", "WATER", "GRASS", "CLOUD", "PAINT", "DANCE", "MUSIC", "HOUSE", "APPLE"],
            "18": ["MAGIC", "POWER", "ROYAL", "GLORY", "HONOR", "TRUTH", "VALUE", "TRUST", "BLEND", "GRAND"]
        }

    def generate_flashcards(self, age: str) -> PhonemeFlashcardsResponse:
        """Generate a phoneme flashcard with a word and its characters based on age-appropriate word length"""
        
        try:
            word = self._generate_word_with_ai(age)
        except Exception as e:
            print(f"AI generation failed for age {age}: {e}")
            age_int = int(age)
            if age_int < 8:
                fallback_ages = ["3", "4", "5", "6", "7"]
            elif age_int < 15:
                fallback_ages = ["8", "9", "10", "11", "12", "13", "14"]
            else:
                fallback_ages = ["15", "16", "17", "18"]
            
            # Pick a random age from the appropriate range and get a word
            fallback_age = random.choice(fallback_ages)
            print(f"Using fallback age {fallback_age} for input age {age}")  # Debug log
            word_list = self.words_by_age.get(fallback_age, self.words_by_age["8"])
            word = random.choice(word_list)
            print(f"Selected word: {word} from fallback_age {fallback_age}")  # Debug log
        
        # Convert word to uppercase and split into characters
        word_upper = word.upper()
        characters = list(word_upper)
        
        return PhonemeFlashcardsResponse(
            word=word_upper,
            characters=characters,
            age=age
        )
    
    def _generate_word_with_ai(self, age: str) -> str:
        """Generate an age-appropriate word using OpenAI with dynamic word length based on age"""
        
        age_int = int(age)
        
        # Determine word length and complexity based on age
        if age_int < 8:
            word_length = "3 letters"
            target_length = 3
            complexity = "very simple"
            examples = "cat, dog, sun, box, hat, pen, cup, bed, red, top"
        elif age_int < 15:
            word_length = "4 letters"
            target_length = 4
            complexity = "simple to moderate"
            examples = "play, jump, tree, bird, walk, talk, game, name"
        else:
            word_length = "5 letters"
            target_length = 5
            complexity = "moderate to complex"
            examples = "plant, dream, beach, heart, world, light, smile, happy"
        
        # Create exclusion list from cache (flatten all previous responses)
        excluded_words = examples.replace(", ", ", ")
        if self.word_cache:
            cached_words = [word for word in self.word_cache]
            excluded_words += ", " + ", ".join(cached_words)
            
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        
        Generate ONE single {complexity} word that is appropriate for {age}-year-old children learning phonics.

        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify the word is NOT in the list!
        
        Requirements:
        - The word MUST be EXACTLY {word_length} long ({target_length} characters only)
        - Use common, familiar words that kids of age {age} would know
        - The word should be easy to sound out and phonetically regular
        - Return ONLY the word in uppercase, nothing else
        - No punctuation, no explanation, just ONE word
        - Make sure the word is exactly {target_length} letters long
        """
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a phonics teacher. Generate a single word of the exact specified length only."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.8
        )
        
        word = response.choices[0].message.content.strip().upper()
        # Remove any punctuation or extra characters
        word = ''.join(c for c in word if c.isalpha())
        
        # Validate word length - if not correct, raise exception to use fallback
        if len(word) != target_length:
            raise ValueError(f"Generated word '{word}' is not {target_length} letters long")
        
        # Update cache with new word (keep last 5 words)
        self.word_cache.append(word)
        self.word_cache = self.word_cache[-5:]
        
        return word