import os
import openai
import random
from dotenv import load_dotenv
from .sight_word_practice_schema import SightWordRequest, SightWordResponse, SightWordItem

load_dotenv()

class SightWordPractice:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.sentence_cache = []     
        self.sight_word_cache = [] 
    
    def generate_sentence(self, request: SightWordRequest) -> SightWordResponse:
        """Generate sight word items with definitions, sentences, and quiz questions"""
        
        age = str(request.age) if request.age else "6"      
        selected_words = self._generate_sight_words_with_ai(age)
        
        sight_word_items = self._generate_sight_word_items_with_ai(selected_words, age)
        
        return SightWordResponse(response=sight_word_items)

    def _generate_sight_words_with_ai(self, age: str) -> list:
        """Generate 5 age-appropriate sight words using AI"""
        
        age_int = int(age)
        if age_int <= 6:
            complexity = "very basic high-frequency words (the, and, a, to, in, is, you, that, it, he)"
            level = "kindergarten to 1st grade"
        elif age_int <= 9:
            complexity = "common high-frequency words (was, for, on, are, as, with, his, they, had, by, but, not)"
            level = "2nd to 3rd grade"
        elif age_int <= 12:
            complexity = "intermediate sight words (each, which, how, their, about, many, would, make, could, people)"
            level = "4th to 5th grade"
        elif age_int <= 15:
            complexity = "advanced sight words (through, because, important, different, thought, together, example, language)"
            level = "6th to 8th grade"
        else:
            complexity = "sophisticated sight words (although, environment, necessary, organization, opportunity, immediately, definitely, experience)"
            level = "high school"
        
        excluded_words = "basic, example, word, sight"
        if self.sight_word_cache:
            cached_words = [word for word_list in self.sight_word_cache for word in word_list]
            excluded_words += ", " + ", ".join(cached_words)
            
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        
        Generate exactly 5 age-appropriate sight words for {age}-year-old learners ({level} level).
        
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list!
        
        Requirements:
        - Select {complexity}
        - Words should be appropriate for {level} reading level
        - Choose high-frequency words that appear often in texts
        - Words should be recognizable by sight (not phonetically decoded)
        - Avoid proper nouns, abbreviations, or overly complex words
        - Make sure words are commonly used in age-appropriate reading materials
        
        Return ONLY a JSON object in this exact format:
        {{
            "words": ["word1", "word2", "word3", "word4", "word5"]
        }}
        
        Do not include any additional text or formatting."""
        
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational expert who selects age-appropriate sight words for reading instruction. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=150
            )
            
            content = completion.choices[0].message.content.strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            import json
            data = json.loads(content)
            sight_words = data.get('words', [])

            if len(sight_words) != 5:
                raise ValueError(f"Expected 5 words, got {len(sight_words)}")

            self.sight_word_cache.append(sight_words)
            self.sight_word_cache = self.sight_word_cache[-5:]
            
            return sight_words
            
        except Exception as e:
            print(f"Error generating sight words: {e}")
            raise

    def _generate_sight_word_items_with_ai(self, sight_words: list, age: str) -> list:
        """Use OpenAI to generate comprehensive sight word items with definitions, sentences, and quizzes"""
        
        words_list = ", ".join(sight_words)
        
        age_guidance = {
            "5": "very simple definitions and sentences for 5-year-olds (kindergarten level)",
            "6": "simple definitions and sentences for 6-year-olds (1st grade level)",
            "7": "moderately simple definitions and sentences for 7-year-olds (2nd grade level)",
            "8": "slightly more complex definitions and sentences for 8-year-olds (3rd grade level)"
        }
        
        complexity = age_guidance.get(age, age_guidance["6"])
        
        excluded_content = "basic examples, simple sentences"
        if self.sentence_cache:
            excluded_content += ", " + ", ".join(self.sentence_cache)
            
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE CREATING ANY CONTENT: {excluded_content}
        
        You are a helpful teacher creating sight word exercises for {age}-year-old children.

        ❌ ABSOLUTE RULE: NEVER create content similar to the exclusion list above. Make everything completely new!
        
        For each of these sight words: {words_list}
        
        Create:
        1. A simple definition (2-5 words) appropriate for {age}-year-olds
        2. An example sentence using the word
        3. A quiz with 3 sentences where the sight word is replaced with a blank (_____). Only ONE sentence should make sense with the sight word.
        4. For the answer field, provide the COMPLETE correct sentence with the sight word filled in (not just the number)
        
        Make it {complexity}
        
        Return ONLY valid JSON in this exact format:
        {{
            "items": [
                {{
                    "word": "the",
                    "definition": ["a word that points to something"],
                    "sentence": "The cat is sleeping.",
                    "quiz": [
                        "_____ dog is running fast.",
                        "I like _____ eat apples.",
                        "She can _____ very well."
                    ],
                    "answer": "the dog is running fast."
                }}
            ]
        }}
        
        Create one item for each word: {words_list}
        """

        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational content creator who generates sight word exercises for children. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            content = completion.choices[0].message.content.strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            import json
            data = json.loads(content)

            sight_word_items = []
            for item_data in data.get('items', []):
                sight_word_items.append(SightWordItem(**item_data))
            
            cache_content = [item.sentence for item in sight_word_items]
            self.sentence_cache.extend(cache_content)
            self.sentence_cache = self.sentence_cache[-5:]
                
            return sight_word_items
            
        except Exception as e:
            print(f"Error generating sight word items: {e}")
            raise
