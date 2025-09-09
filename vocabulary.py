# using fugashi to tokenize Japanese text
import fugashi
import requests
from dotenv import load_dotenv
import os
from urllib.parse import quote

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
    tagger = fugashi.Tagger()
    # set a list to hold raw tokens
    raw_token = []
    for word in tagger(text):
        if word.surface in {"、", "。", "！", "？"}:
            continue
        if word.feature.pos1 in ["助詞", "助動詞", "感動詞"]:
            continue
        lemma = word.feature.lemma if word.feature.lemma != "*" else word.surface
        raw_token.append(lemma)
    
    # set seen status for seen words
    seen = set()

    # set a list to hold unique tokens
    token = []

    for word in raw_token:
        # remove words that are just a hiragana character
        if len(word) == 1 and hiragana_char(word):
            continue  
        # remove duplicates
        if word in seen:
            continue

        seen.add(word)
        # add word to token list
        token.append(word)
        
    return token

def vocabulary_extraction(word_list):
    vocabulary_list = {
        "N5": [],
        "N4": [],
        "N3": [],
        "N2": [],
        "N1": []
    }
    
    for word in word_list:
        w = quote(word, safe="")

        # Try kanji first
        url_kanji = f"{SUPABASE_URL}/rest/v1/jlptvocabulary?kanji=eq.{w}&select=hiragana,kanji,english,level&limit=1"
        response = requests.get(url_kanji, headers=headers)

        data = []
        if response.status_code == 200:
            data = response.json()

        # If no kanji match, try hiragana
        if not data:
            url_hira = f"{SUPABASE_URL}/rest/v1/jlptvocabulary?hiragana=eq.{w}&select=hiragana,kanji,english,level&limit=1"
            response = requests.get(url_hira, headers=headers)
            if response.status_code == 200:
                data = response.json()

        if data:
            result = data[0]
            level = result.get("level", "").upper()
            kanji = result.get("kanji", "")
            hiragana = result.get("hiragana", "")            
            english = result.get("english", "")
            
            if level and level in vocabulary_list:
                vocabulary_list[level].append({
                    "Word": kanji if kanji else hiragana,  # prefer kanji display
                    "Pronunciation": hiragana,
                    "Meaning": english
                })
    
    return vocabulary_list

""" testing using database to categorize vocabulary
# using a database to categorize vocabulary
def categorize_word(word_list):
    connection = sqlite3.connect("JLPTvocabulary.db")
    cursor = connection.cursor()

    categorized = {
        "N5": [],
        "N4": [],
        "N3": [],
        "N2": [],
        "N1": []
    }
    for word in word_list:
        cursor.execute("SELECT level FROM JLPTVocabulary WHERE hiragana = ? OR kanji = ?", (word, word))
        result = cursor.fetchone()
        if result:
            level = result[0]
            categorized[level].append(f"{word}")
        #else:
            #categorized.append(f"Word: {word} not in the database.")
    
    connection.close()
    return categorized
"""
""" testing using database to find the pronounciation and meaning
# using a dictionary to find the pronounciation and meaning
def vocab(word_list):
    connection = sqlite3.connect("JLPTVocabulary.db")
    cursor = connection.cursor()

    vocabulary_list = []

    for word in word_list:
        cursor.execute("SELECT hiragana, english FROM JLPTVocabulary where kanji = ?", (word,))
        result = cursor.fetchone()
        if result:
            hiragana, english = result
            vocabulary_list.append({
                "Word": word,
                "Pronunciation": hiragana,
                "Meaning": english
            })

    connection.close()
    return vocabulary_list
"""
