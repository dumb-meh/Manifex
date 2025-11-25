#!/usr/bin/env python3

# Test script to debug phoneme flashcards
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.services.Reading.phoneme_flashcards.phoneme_flashcards import PhonemeFlashcards

def test_age_16():
    print("Testing phoneme flashcards with age 16...")
    
    # Create instance
    service = PhonemeFlashcards()
    
    # Test the generate_flashcards method
    try:
        result = service.generate_flashcards("16")
        print(f"Result for age 16: {result}")
        print(f"Word: {result.word}")
        print(f"Word length: {len(result.word)}")
        print(f"Age in response: {result.age}")
        
        if len(result.word) != 5:
            print(f"ERROR: Expected 5-letter word for age 16, got {len(result.word)}-letter word: {result.word}")
        else:
            print("SUCCESS: Got correct 5-letter word for age 16")
            
    except Exception as e:
        print(f"Error: {e}")

def test_ai_generation():
    print("\nTesting AI generation directly...")
    
    service = PhonemeFlashcards()
    
    try:
        word = service._generate_word_with_ai("16")
        print(f"AI generated word for age 16: {word}")
        print(f"Word length: {len(word)}")
        
        if len(word) != 5:
            print(f"ERROR: AI generated {len(word)}-letter word instead of 5-letter word")
        else:
            print("SUCCESS: AI generated correct 5-letter word")
            
    except Exception as e:
        print(f"AI generation failed: {e}")

if __name__ == "__main__":
    test_age_16()
    test_ai_generation()