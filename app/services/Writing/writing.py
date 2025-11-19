import os
import json
import openai
import random
import re
from dotenv import load_dotenv
from .writing_schema import InitialTopicResponse, FinalScoreRequest, FinalScoreResponse, TopicRequest

load_dotenv ()

class Writing:
    def __init__(self):
        self.client=openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.available_topics = [
            "Sports", "Dance", "Cooking", "Food", "Nature", 
            "Art", "Music", "Travel", "Science", "Movies", 
            "Meditation", "Gaming", "Animals"
        ]

    def get_topic(self, topic_request: TopicRequest = None) -> InitialTopicResponse:
        # Use provided topic or randomly select one if not provided
        if topic_request and topic_request.topic:
            selected_topic = topic_request.topic.value
        else:
            selected_topic = random.choice(self.available_topics)
        
        # Create prompt to get 5 related words for the selected topic
        prompt = f"""You are a helpful assistant that provides exactly 5 related words for a given topic. 
        Provide exactly 5 words related to the topic '{selected_topic}'. 
        Return only the 5 words separated by commas, nothing else.
        The words should be simple and commonly used words related to the topic."""
        
        # Get AI response for related words
        response = self.get_openai_response(prompt, selected_topic)
        
        # Parse the response to extract the 5 words
        related_words = [word.strip().rstrip('.') for word in response.split(',')]
        
        # Ensure we have exactly 5 words
        if len(related_words) > 5:
            related_words = related_words[:5]
        elif len(related_words) < 5:
            # If we get fewer than 5 words, pad with generic topic-related words
            while len(related_words) < 5:
                related_words.append(f"{selected_topic.lower()}_related")
        
        return InitialTopicResponse(topic=selected_topic, related_words=related_words)
    
    def get_writing_score(self, input_data: FinalScoreRequest) -> FinalScoreResponse:
        # Analyze word usage
        words_used = self._check_word_usage(input_data.user_paragraph, input_data.related_words)
        word_usage_score = min(len(words_used) * 2, 10)  # 2 points per word used, max 10
        
        # Get grammar and sentence quality score from AI
        grammar_score = self._get_grammar_score(input_data.user_paragraph, input_data.topic)
        
        # Combined sentence score (grammar + word usage, out of 10)
        sentence_score = min(round((grammar_score + word_usage_score) / 2), 10)
        
        # Get motivation message
        motivation = self._get_motivation_message(
            input_data.user_paragraph, 
            input_data.topic, 
            input_data.related_words,
            words_used, 
            sentence_score
        )
        
        return FinalScoreResponse(
            sentence_score=sentence_score,
            motivation=motivation
        )
    
    def _check_word_usage(self, paragraph: str, related_words: list) -> list:
        """Check which related words are used in the paragraph"""
        words_used = []
        paragraph_lower = paragraph.lower()
        
        for word in related_words:
            # Check for exact word match (case-insensitive)
            word_pattern = r'\b' + re.escape(word.lower()) + r'\b'
            if re.search(word_pattern, paragraph_lower):
                words_used.append(word)
        
        return words_used
    
    def _get_grammar_score(self, paragraph: str, topic: str) -> int:
        """Get grammar and sentence quality score from AI (0-10)"""
        prompt = f"""You are an English writing evaluator. Score the following paragraph on grammar, sentence structure, and overall quality on a scale of 0-10.

Consider:
- Grammar correctness
- Sentence structure and flow
- Vocabulary usage
- Relevance to the topic: {topic}
- Overall coherence and clarity

Return ONLY a number from 0 to 10. Nothing else."""

        try:
            response = self.get_openai_response(prompt, paragraph)
            # Extract number from response
            score_match = re.search(r'\d+', response)
            if score_match:
                score = int(score_match.group())
                return min(max(score, 0), 10)  # Ensure score is between 0-10
            return 5  # Default score if parsing fails
        except:
            return 5  # Default score on error
    
    def _get_motivation_message(self, paragraph: str, topic: str, related_words: list, 
                               words_used: list, sentence_score: int) -> str:
        """Get encouraging motivation message from AI"""
        
        words_used_count = len(words_used)
        total_words = len(related_words)
        
        motivation_prompt = f"""Create a very short, encouraging motivational message for a student who wrote about {topic}.

Student's writing score: {sentence_score}/10
Words used from provided list: {words_used_count}/{total_words}

Be positive and encouraging. 
IMPORTANT: Use EXACTLY 10 words. No more, no less. Count carefully.
Example format: "Great job writing! Keep practicing and you will improve greatly!"

Respond with only the 10-word message."""

        try:
            motivation = self.get_openai_response(motivation_prompt, paragraph)
            # Ensure exactly 10 words
            words = motivation.strip().split()
            if len(words) > 10:
                motivation = ' '.join(words[:10])
            elif len(words) < 10:
                # Pad with encouraging words if needed
                padding_words = ["Keep", "going!", "You", "can", "do", "it!", "Practice", "more!", "Stay", "motivated!"]
                while len(words) < 10:
                    words.append(padding_words[len(words) % len(padding_words)])
                motivation = ' '.join(words[:10])
            return motivation
        except:
            # Fallback messages with exactly 10 words each
            if sentence_score >= 7:
                return "Excellent work! Your writing shows great skill and creativity today."
            elif sentence_score >= 5:
                return "Good job! Keep practicing and you will continue improving greatly."
            else:
                return "Great effort! Every word you write makes you better daily."
    
    def create_prompt(self) -> str:
        return f""""""
                
    def get_openai_response (self, prompt:str, data:str)->str:
        completion =self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"system", "content": prompt},{"role":"user", "content": data}],
            temperature=0.7            
        )
        return completion.choices[0].message.content