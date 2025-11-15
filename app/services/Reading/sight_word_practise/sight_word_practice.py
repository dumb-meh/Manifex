import os
import openai
import random
from dotenv import load_dotenv
from .sight_word_practice_schema import SightWordRequest, SightWordResponse

load_dotenv()

class SightWordPractice:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Common sight words organized by grade level
        self.sight_words_by_grade = {
            "1": [
                "the", "and", "a", "to", "in", "is", "you", "that", "it", "he",
                "was", "for", "on", "are", "as", "with", "his", "they", "I", "at",
                "be", "this", "have", "from", "or", "one", "had", "by", "but", "not",
                "what", "all", "were", "we", "when", "your", "can", "said", "there", "use"
            ],
            "2": [
                "each", "which", "she", "do", "how", "their", "if", "will", "up", "other",
                "about", "out", "many", "then", "them", "these", "so", "some", "her", "would",
                "make", "like", "him", "into", "time", "has", "look", "two", "more", "write",
                "go", "see", "number", "no", "way", "could", "people", "my", "than", "first"
            ],
            "3": [
                "water", "been", "call", "who", "oil", "its", "now", "find", "long", "down",
                "day", "did", "get", "come", "made", "may", "part", "over", "new", "sound",
                "take", "only", "little", "work", "know", "place", "year", "live", "me", "back",
                "give", "most", "very", "after", "thing", "our", "just", "name", "good", "sentence"
            ]
        }
    
    def generate_sentence(self, request: SightWordRequest) -> SightWordResponse:
        """Generate a sentence containing specified sight words"""
        
        # Validate and get grade level
        grade_level = str(request.grade_level) if request.grade_level else "1"
        if grade_level not in self.sight_words_by_grade:
            grade_level = "1"
        
        # Get number of words to include
        num_words = min(max(request.num_words, 2), 5) if request.num_words else 3
        
        # Randomly select sight words from the grade level
        available_words = self.sight_words_by_grade[grade_level]
        selected_words = random.sample(available_words, min(num_words, len(available_words)))
        
        # Generate sentence using OpenAI
        sentence = self._generate_sentence_with_ai(selected_words, grade_level)
        
        return SightWordResponse(
            sentence=sentence,
            sight_words=selected_words,
            grade_level=grade_level
        )
    
    def _generate_sentence_with_ai(self, sight_words: list, grade_level: str) -> str:
        """Use OpenAI to generate a natural sentence containing the sight words"""
        
        words_list = ", ".join(sight_words)
        
        prompt = f"""You are a helpful teacher creating practice sentences for grade {grade_level} students.

Create a simple, natural, and age-appropriate sentence that includes ALL of these sight words: {words_list}

Requirements:
- The sentence MUST use ALL the provided words: {words_list}
- Make it simple and appropriate for grade {grade_level} students
- The sentence should be natural and make sense
- Use correct grammar and punctuation
- Keep it between 8-15 words long
- Make it engaging and fun for kids

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
                
            return sentence
            
        except Exception as e:
            # Fallback: create a simple sentence if AI fails
            return f"The student can {sight_words[0]} and {sight_words[1] if len(sight_words) > 1 else 'learn'}."
