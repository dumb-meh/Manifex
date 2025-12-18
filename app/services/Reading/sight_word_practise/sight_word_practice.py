import os
import openai
import random
from dotenv import load_dotenv
from .sight_word_practice_schema import SightWordRequest, SightWordResponse, SightWordItem
from app.utils.text_to_speech import generate_parallel_audio_files

load_dotenv()

class SightWordPractice:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.sentence_cache = []     
        self.sight_word_cache = [] 
    
    async def generate_sentence(self, request: SightWordRequest) -> SightWordResponse:
        """Generate sight word items with definitions, sentences, and quiz questions"""
        
        age = str(request.age) if request.age else "6"      
        selected_words = self._generate_sight_words_with_ai(age)
        
        # Generate audio for each sight word
        audio_urls = await generate_parallel_audio_files(selected_words, prefix="sight_word")
        
        sight_word_items = self._generate_sight_word_items_with_ai(selected_words, age, audio_urls)
        
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

    def _generate_sight_word_items_with_ai(self, sight_words: list, age: str, audio_urls: list) -> list:
        """Use OpenAI to generate comprehensive sight word items with definitions, sentences, and quizzes"""
        
        # Step 1: Generate base info (definition + example sentence) for each sight word
        base_items = self._generate_base_info(sight_words, age)
        
        # Step 2: For each word, generate correct quiz sentence and wrong options in parallel
        sight_word_items = []
        
        for i, word in enumerate(sight_words):
            base_info = base_items[i]
            
            # Generate correct sentence using the word and wrong sentences avoiding the word
            correct_sentence_blank, correct_sentence_filled = self._generate_correct_sentence(word, age)
            wrong_sentences = self._generate_wrong_sentences_avoiding_word(word, age, 2)
            
            # Randomly shuffle quiz options (use blank version for quiz)
            import random
            quiz = [correct_sentence_blank] + wrong_sentences
            random.shuffle(quiz)
            
            # Create the final item
            sight_word_items.append(SightWordItem(
                word=word,
                audio_url=audio_urls[i] if i < len(audio_urls) else "",
                definition=base_info['definition'],
                sentence=base_info['example_sentence'],
                quiz=quiz,
                answer=correct_sentence_filled
            ))
        
        # Cache sentences
        cache_content = [item.sentence for item in sight_word_items]
        self.sentence_cache.extend(cache_content)
        self.sentence_cache = self.sentence_cache[-25:]
        
        return sight_word_items
    
    def _generate_base_info(self, sight_words: list, age: str) -> list:
        """Generate definition and example sentence for each sight word"""
        
        words_list = ", ".join(sight_words)
        
        prompt = f"""For each sight word: {words_list}

Create:
1. A simple definition (2-5 words) appropriate for {age}-year-old children
2. An example sentence using the word

Return JSON:
{{
  "items": [
    {{
      "word": "the",
      "definition": ["points to something"],
      "example_sentence": "The cat is sleeping."
    }}
  ]
}}

Create items for: {words_list}"""

        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational content creator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
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
            return data.get('items', [])
            
        except Exception as e:
            print(f"Error generating base info: {e}")
            raise
    
    def _generate_correct_sentence(self, word: str, age: str) -> str:
        """Generate a quiz sentence using the specific sight word"""
        
        prompt = f"""Create ONE simple sentence for {age}-year-old children that uses the word "{word}".

The sentence should have a blank _____ where "{word}" goes.

Example for word "was":
"She _____ happy yesterday."

Return JSON:
{{
  "sentence": "She _____ happy yesterday."
}}

Create sentence for word: {word}"""

        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational content creator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
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
            sentence_with_blank = data.get('sentence', '')
            sentence_filled = sentence_with_blank.replace('_____', word)
            # Return both versions: (with blank for quiz, filled for answer)
            return sentence_with_blank, sentence_filled
            
        except Exception as e:
            print(f"Error generating correct sentence: {e}")
            raise
    
    def _generate_wrong_sentences_avoiding_word(self, word_to_avoid: str, age: str, count: int) -> list:
        """Generate sentences that specifically DO NOT use the given sight word"""
        
        prompt = f"""Generate {count} simple sentences for {age}-year-old children.

Each sentence should have _____ in place of a word.

🚨 CRITICAL: The blank should be for a word that is NOT "{word_to_avoid}".
The sentences should need words like: am, is, are, go, run, jump, sit, eat, like, want, etc.

DO NOT create sentences where "{word_to_avoid}" would fit in the blank!

Example if avoiding "was":
✗ BAD: "She _____ very happy." (this can work both for "is" and "was" - DO NOT create this!)
✓ GOOD: "I _____ to play outside." (needs "like", not "was")
✗ BAD: "She _____ tired yesterday." (this needs "was" - DO NOT create this!)

Return JSON:
{{
  "sentences": [
    "She _____ very happy.",
    "I _____ to play outside."
  ]
}}

Generate {count} sentences that DO NOT need the word "{word_to_avoid}"."""

        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational content creator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=200
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
            return data.get('sentences', [])
            
        except Exception as e:
            print(f"Error generating wrong sentences: {e}")
            raise
