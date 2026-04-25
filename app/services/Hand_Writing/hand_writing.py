import os
import base64
import json
from openai import OpenAI
from app.services.Hand_Writing.hand_writing_schema import HandWritingResponse, HandWritingWordsResponse
from fastapi import UploadFile


class HandWritingChecker:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
        # Keep last 5 generated batches per user to avoid repetition, matching existing cache pattern in project.
        self.word_cache = {}
        
    async def check_handwriting(self, image_file: UploadFile, word: str) -> HandWritingResponse:
        """
        Check if the handwritten text in the image matches the provided word
        """
        try:
            # Read and encode the image
            image_data = await image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Determine image format
            content_type = image_file.content_type or "image/jpeg"
            
            # Create prompt for GPT-4 Vision
            prompt = f"""
            Analyze this image and extract any handwritten text you can see.
            
            Then compare the extracted text with this word: "{word}"
            
            Respond with ONLY a JSON object in this exact format:
            {{
                "matches": true or false
            }}
            
            The match should be case-insensitive and ignore minor spelling variations if the intent is clear.
            """
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Parse the response
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            import json
            result = json.loads(result_text)
            
            matches = result.get('matches', False)
            
            return HandWritingResponse(correct=matches)
            
        except Exception as e:
            print(f"Error checking handwriting: {e}")
            return HandWritingResponse(correct=False)
        
        
    async def get_handwriting_words(self, user_id: str) -> HandWritingWordsResponse:
        if user_id not in self.word_cache:
            self.word_cache[user_id] = []

        excluded_words = "cat, dog, sun, tree"
        if self.word_cache[user_id]:
            cached_words = [word for batch in self.word_cache[user_id] for word in batch]
            excluded_words += ", " + ", ".join(cached_words)

        prompt = f"""
        You are creating handwriting practice words for children.

        ⚠️ FIRST: CHECK THIS EXCLUSION LIST BEFORE SELECTING ANY WORDS: {excluded_words}
        ❌ ABSOLUTE RULE: NEVER use words from the exclusion list above. Verify EACH word is NOT in the list.

                Requirements:
                - Return exactly 10 UNIQUE words in this exact order:
                    1) first 4 words are easy (exactly 3 letters)
                    2) next 3 words are medium (exactly 4 letters)
                    3) last 3 words are hard (5 or more letters)
        - Use common kid-friendly English words
        - No proper nouns, abbreviations, or rare words

        Return ONLY valid JSON in this exact format:
        {{
            "words": ["cat", "sun", "dog", "pen", "book", "tree", "fish", "planet", "rocket", "animal"]
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )

        result_text = response.choices[0].message.content.strip()
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]
        result_text = result_text.strip()

        parsed = json.loads(result_text)
        raw_words = parsed.get("words", [])
        if isinstance(raw_words, list):
            generated_words = [str(w).strip().lower() for w in raw_words if str(w).strip()]
        else:
            generated_words = [w.strip().lower() for w in str(raw_words).split(",") if w.strip()]

        if len(generated_words) != 10:
            raise ValueError("Failed to generate exactly 10 words")

        if len(set(generated_words)) != 10:
            raise ValueError("Generated words contain duplicates")

        cached_seen = set([word.lower() for batch in self.word_cache[user_id] for word in batch])
        if any(word in cached_seen for word in generated_words):
            raise ValueError("Generated words repeated cached words")

        # Validate difficulty by position: first 4 easy (3 letters), next 3 medium (4), last 3 hard (5+).
        easy_words = generated_words[:4]
        medium_words = generated_words[4:7]
        hard_words = generated_words[7:10]

        if not all(len(word) == 3 for word in easy_words):
            raise ValueError("First 4 words must be easy (3 letters)")
        if not all(len(word) == 4 for word in medium_words):
            raise ValueError("Next 3 words must be medium (4 letters)")
        if not all(len(word) >= 5 for word in hard_words):
            raise ValueError("Last 3 words must be hard (5+ letters)")

        self.word_cache[user_id].append(generated_words)
        self.word_cache[user_id] = self.word_cache[user_id][-5:]

        return HandWritingWordsResponse(words=generated_words)

    async def check_handwriting_words(self, image_file: UploadFile, word: str) -> HandWritingResponse:
        """
        Check if the handwritten text in the image matches the provided word
        """
        try:
            # Read and encode the image
            image_data = await image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Determine image format
            content_type = image_file.content_type or "image/jpeg"
            
            # Create prompt for GPT-4 Vision
            prompt = f"""
            Analyze this image and extract any handwritten text you can see.

            Then compare the extracted text with this word: "{word}"

            Respond with ONLY a JSON object in this exact format:
            {{
                "matches": true or false
            }}

            The match should be case-insensitive and ignore minor spelling variations if the intent is clear.
            """
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            # Parse the response
            result_text = response.choices[0].message.content.strip()
            
            # Clean JSON response
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)

            matches = result.get('matches', False)
            return HandWritingResponse(correct=matches)
            
        except Exception as e:
            print(f"Error checking handwriting: {e}")
            return HandWritingResponse(correct=False)
            
    

        
    
    