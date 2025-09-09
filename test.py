import fugashi
import requests
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

headers = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

def hiragana_char(char):
    return '\u3040' <= char <= '\u309F'

def tokenize_word(text: str):
    print(f"Tokenizing text: {text}")
    tagger = fugashi.Tagger()
    
    # Use word.surface instead of word.feature.lemma to fix the lemma issue
    raw_token = [
        word.surface  # Changed from word.feature.lemma
        for word in tagger(text) 
        if word.surface not in {"。", "、", "！", "？"}
        ] 
    
    print(f"Raw tokens: {raw_token}")
    
    seen = set()
    token = []

    for word in raw_token:
        if len(word) == 1 and hiragana_char(word):
            continue  
        if word in seen:
            continue
        seen.add(word)
        token.append(word)
    
    print(f"Final tokens: {token}")
    return token

def vocabulary_extraction(word_list):
    print(f"Starting vocabulary extraction for: {word_list}")
    vocabulary_list = {
        "N5": [],
        "N4": [],
        "N3": [],
        "N2": [],
        "N1": []
    }
    
    for word in word_list:
        print(f"Processing word: {word}")
        
        url = f"{SUPABASE_URL}/rest/v1/jlptvocabulary" \
              f"?or=(hiragana.eq.{word},kanji.eq.{word})"\
              f"&select=hiragana,kanji,english,level"\
              f"&limit=1"
        
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    level = result.get("level", "").upper()
                    kanji = result.get("kanji", "")
                    hiragana = result.get("hiragana", "")            
                    english = result.get("english", "")
                    
                    print(f"Found: {hiragana} / {kanji} = {english} ({level})")
                    
                    if level and level in vocabulary_list:
                        vocabulary_list[level].append({
                            "Word": word,
                            "Pronunciation": hiragana,
                            "Meaning": english
                        })
                        print(f"✅ Added {word} to {level}")
                    else:
                        print(f"❌ Level '{level}' not in vocabulary_list")
                else:
                    print(f"❌ No match found for: {word}")
            except Exception as e:
                print(f"❌ Error processing {word}: {e}")
                
    return vocabulary_list

def test_specific_words():
    """Test with words we know exist in the database"""
    print("=== Testing with known words from database ===")
    
    # These words are from your sample data
    test_words = ["よろしい", "宜しい", "たから", "宝", "み", "実"]
    
    vocab_result = vocabulary_extraction(test_words)
    print(f"\nResult for known words: {vocab_result}")

def test_with_japanese_sentence():
    """Test with actual Japanese sentence"""
    print("\n=== Testing with Japanese sentence ===")
    
    # Use a sentence with words that might be in your database
    test_text = "実は宝を見つけました"
    tokens = tokenize_word(test_text)
    vocab_result = vocabulary_extraction(tokens)
    
    print(f"\nFinal result: {vocab_result}")

if __name__ == "__main__":
    print("🧪 TESTING WITH EXISTING DATABASE DATA\n")
    
    # Test 1: Known words
    test_specific_words()
    
    # Test 2: Real sentence
    test_with_japanese_sentence()