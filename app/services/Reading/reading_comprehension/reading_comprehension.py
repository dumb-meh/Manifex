import os 
import openai
import json
from dotenv import load_dotenv
from .reading_comprehension_schema import ReadingComprehensionResponse, QuestionAnswer

load_dotenv()

class ReadingComprehension:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.passage_cache = []  # Cache for last 5 generated reading passages

    def generate_comprehension(self, age: str) -> ReadingComprehensionResponse:
        """Generate age-appropriate reading comprehension passage with questions and answers"""
        
        # Age-appropriate complexity levels
        age_guidance = {
            "5": {"level": "very simple", "words": "50-80", "grade": "kindergarten"},
            "6": {"level": "simple", "words": "80-120", "grade": "1st grade"},
            "7": {"level": "moderately simple", "words": "120-150", "grade": "2nd grade"},
            "8": {"level": "slightly complex", "words": "150-200", "grade": "3rd grade"}
        }
        
        guidance = age_guidance.get(age, age_guidance["6"])
        
        # Create exclusion list from cache (flatten all previous passages)
        excluded_topics = "friendly cat, garden adventure, butterfly chase"
        if self.passage_cache:
            cached_topics = [passage.get('passage_name', '') for passage in self.passage_cache if passage.get('passage_name')]
            if cached_topics:
                excluded_topics += ", " + ", ".join(cached_topics)
        
        prompt = f"""⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE CREATING ANY CONTENT: {excluded_topics}
        
        You are an educational content creator. Generate a complete reading comprehension exercise for {age}-year-old children ({guidance['grade']} level).

        ❌ ABSOLUTE RULE: NEVER use topics or titles from the exclusion list above. Verify your content is completely new!
        
        Create:
        1. A short, engaging passage ({guidance['words']} words) that is {guidance['level']} and age-appropriate
        2. A creative title for the passage (NOT from exclusion list)
        3. Exactly 3 multiple-choice comprehension questions about the passage
        4. For each question, provide exactly 3 options and indicate which one is correct

        The passage should:
        - Be interesting and relatable for {age}-year-olds
        - Use appropriate vocabulary for {guidance['grade']} level
        - Have a clear beginning, middle, and end
        - Cover topics kids enjoy (animals, adventures, friends, family, nature, etc.)

Format your response EXACTLY as JSON:
{{
  "passage_name": "Title of the passage",
  "text": "The full passage text here",
  "questions": [
    {{
      "question": "First question?",
      "options": ["Option 1", "Option 2", "Option 3"],
      "correct_answer": "Option 1"
    }},
    {{
      "question": "Second question?",
      "options": ["Option A", "Option B", "Option C"],
      "correct_answer": "Option B"
    }},
    {{
      "question": "Third question?",
      "options": ["Choice 1", "Choice 2", "Choice 3"],
      "correct_answer": "Choice 3"
    }}
  ]
}}

IMPORTANT: 
- Each question must have EXACTLY 3 options
- The correct_answer must be one of the options provided
- Make the options plausible but clearly distinguishable

Return ONLY valid JSON, nothing else."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational content creator who generates reading comprehension materials for children. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.8
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            # Parse JSON response
            data = json.loads(content)
            
            # Convert to proper schema format
            questions = [QuestionAnswer(**q) for q in data["questions"]]
            
            # Update cache with new passage (keep last 5 responses)
            self.passage_cache.append({
                'passage_name': data["passage_name"],
                'text': data["text"]
            })
            self.passage_cache = self.passage_cache[-5:]
            
            # Generate image based on the passage
            image_url = self._generate_image(data["passage_name"], data["text"], age)
            
            return ReadingComprehensionResponse(
                passage_name=data["passage_name"],
                text=data["text"],
                questions=questions,
                age=age,
                image=image_url
            )
            
        except Exception as e:
            # Fallback response if AI fails
            return ReadingComprehensionResponse(
                passage_name="The Friendly Cat",
                text="There was a small cat named Fluffy. Fluffy liked to play in the garden. She would chase butterflies and climb trees. One day, Fluffy made a new friend.",
                questions=[
                    QuestionAnswer(
                        question="What was the cat's name?",
                        options=["Fluffy", "Mittens", "Whiskers"],
                        correct_answer="Fluffy"
                    ),
                    QuestionAnswer(
                        question="Where did Fluffy like to play?",
                        options=["In the house", "In the garden", "At the park"],
                        correct_answer="In the garden"
                    ),
                    QuestionAnswer(
                        question="What did Fluffy do one day?",
                        options=["Took a nap", "Made a new friend", "Ate food"],
                        correct_answer="Made a new friend"
                    )
                ],
                age=age,
                image=""
            )
    
    def _generate_image(self, passage_name: str, passage_text: str, age: str) -> str:
        """Generate a child-friendly illustration for the passage using DALL-E"""
        
        try:
            # Create a prompt for child-friendly illustration
            image_prompt = f"""Create a colorful, child-friendly, cartoon-style illustration for a children's story titled "{passage_name}". 
            
The illustration should depict: {passage_text[:200]}

Style requirements:
- Bright, cheerful colors
- Simple, cute cartoon style appropriate for {age}-year-old children
- Safe, friendly, and educational
- No text or words in the image
- Clear and easy to understand
- Engaging and fun for kids"""

            # Generate image using DALL-E
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            # Return the image URL
            return response.data[0].url
            
        except Exception as e:
            print(f"Image generation error: {str(e)}")
            # Return empty string if image generation fails
            return ""