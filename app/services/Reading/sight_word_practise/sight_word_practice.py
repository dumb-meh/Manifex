import os
import openai
import random
from dotenv import load_dotenv
from .sight_word_practice_schema import SightWordRequest, SightWordResponse

load_dotenv()

class SightWordPractice:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.sentence_cache = []  # Cache for last 5 generated sentences
        
        # Common sight words organized by age
        self.sight_words_by_age = {
            "5": [
                "the", "and", "a", "to", "in", "is", "you", "that", "it", "he",
                "I", "at", "be", "this", "have", "from", "or", "one", "we", "can"
            ],
            "6": [
                "the", "and", "a", "to", "in", "is", "you", "that", "it", "he",
                "was", "for", "on", "are", "as", "with", "his", "they", "I", "at",
                "be", "this", "have", "from", "or", "one", "had", "by", "but", "not",
                "what", "all", "were", "we", "when", "your", "can", "said", "there", "use"
            ],
            "7": [
                "each", "which", "she", "do", "how", "their", "if", "will", "up", "other",
                "about", "out", "many", "then", "them", "these", "so", "some", "her", "would",
                "make", "like", "him", "into", "time", "has", "look", "two", "more", "write",
                "go", "see", "number", "no", "way", "could", "people", "my", "than", "first"
            ],
            "8": [
                "water", "been", "call", "who", "oil", "its", "now", "find", "long", "down",
                "day", "did", "get", "come", "made", "may", "part", "over", "new", "sound",
                "take", "only", "little", "work", "know", "place", "year", "live", "me", "back",
                "give", "most", "very", "after", "thing", "our", "just", "name", "good", "sentence"
            ]
        }
    
    def generate_sentence(self, request: SightWordRequest) -> SightWordResponse:
        """Generate a sentence containing specified sight words"""
        
        # Validate and get age
        age = str(request.age) if request.age else "6"
        if age not in self.sight_words_by_age:
            # Default to closest age if not exact match
            try:
                age_int = int(age)
                if age_int < 6:
                    age = "5"
                elif age_int > 8:
                    age = "8"
                else:
                    age = "6"
            except:
                age = "6"
        
        # Always use 3 sight words
        num_words = 3
        
        # Randomly select sight words from the age group
        available_words = self.sight_words_by_age[age]
        selected_words = random.sample(available_words, min(num_words, len(available_words)))
        
        # Generate sentence using OpenAI
        sentence = self._generate_sentence_with_ai(selected_words, age)
        
        return SightWordResponse(
            sentence=sentence,
            sight_words=selected_words,
            age=age
        )
    
    def _generate_sentence_with_ai(self, sight_words: list, age: str) -> str:
        """Use OpenAI to generate a natural sentence containing the sight words"""
        
        words_list = ", ".join(sight_words)
        
        # Age-appropriate complexity levels
        age_guidance = {
            "5": "very simple sentences with basic vocabulary for 5-year-olds (kindergarten level)",
            "6": "simple sentences with easy vocabulary for 6-year-olds (1st grade level)",
            "7": "moderately simple sentences with broader vocabulary for 7-year-olds (2nd grade level)",
            "8": "slightly more complex sentences with richer vocabulary for 8-year-olds (3rd grade level)"
        }
        
        complexity = age_guidance.get(age, age_guidance["6"])
        
        # Create exclusion list from cache (previous sentences)
        excluded_sentences = "The student can see and learn."
        if self.sentence_cache:
            excluded_sentences += ", " + ", ".join(self.sentence_cache)
            
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE CREATING ANY SENTENCES: {excluded_sentences}
        
        You are a helpful teacher creating practice sentences for {age}-year-old children.

        ❌ ABSOLUTE RULE: NEVER create sentences similar to those in the exclusion list above. Verify your sentence is completely new!
        
        Create a simple, natural, and age-appropriate sentence that includes ALL of these sight words: {words_list}

        Requirements:
        - The sentence MUST use ALL the provided words: {words_list}
        - Make it {complexity}
        - The sentence should be natural and make sense
        - Use correct grammar and punctuation
        - Keep it between 8-15 words long
        - Make it engaging and fun for {age}-year-old kids
        - Use topics and themes that {age}-year-olds can relate to

        Return ONLY the sentence, nothing else."""

        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a creative teacher who makes fun practice sentences for children."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=100
            )
            
            sentence = completion.choices[0].message.content.strip()
            
            # Remove quotes if AI wrapped the sentence in them
            sentence = sentence.strip('"').strip("'")
            
            # Ensure first letter is capitalized and sentence ends with punctuation
            if sentence and not sentence[0].isupper():
                sentence = sentence[0].upper() + sentence[1:]
            if sentence and sentence[-1] not in '.!?':
                sentence += '.'
            
            # Update cache with new sentence (keep last 5 sentences)
            self.sentence_cache.append(sentence)
            self.sentence_cache = self.sentence_cache[-5:]
                
            return sentence
            
        except Exception as e:
            # Fallback: create a simple sentence if AI fails
            return f"The student can {sight_words[0]} and {sight_words[1] if len(sight_words) > 1 else 'learn'}."
