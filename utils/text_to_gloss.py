import logging
import re
import os
import json

logger = logging.getLogger(__name__)

# Path to the custom translation rules file
TRANSLATION_RULES_FILE = os.path.join(os.path.dirname(__file__), 'translation_rules.json')

# Default English to ISL gloss mapping
DEFAULT_ENGLISH_TO_ISL_MAPPING = {
    # Common words
    "hello": "NAMASTE",
    "hi": "NAMASTE",
    "goodbye": "BYE",
    "bye": "BYE",
    "yes": "YES",
    "no": "NO",
    "thank you": "THANK-YOU",
    "thanks": "THANK-YOU",
    "please": "PLEASE",
    "sorry": "SORRY",
    
    # Pronouns
    "i": "I",
    "me": "I",
    "my": "MY",
    "mine": "MY",
    "you": "YOU",
    "your": "YOUR",
    "he": "HE",
    "him": "HE",
    "his": "HIS",
    "she": "SHE",
    "her": "SHE",
    "hers": "HER",
    "we": "WE",
    "us": "WE",
    "our": "OUR",
    "they": "THEY",
    "them": "THEY",
    "their": "THEIR",
    
    # Question words
    "what": "WHAT",
    "when": "WHEN",
    "where": "WHERE",
    "who": "WHO",
    "why": "WHY",
    "how": "HOW",
    
    # Common verbs
    "am": "BE",
    "is": "IS",
    "are": "BE",
    "was": "BE-PAST",
    "were": "BE-PAST",
    "go": "GO",
    "going": "GO",
    "went": "GO-PAST",
    "come": "COME",
    "coming": "COME",
    "came": "COME-PAST",
    "eat": "EAT",
    "eating": "EAT",
    "ate": "EAT-PAST",
    "drink": "DRINK",
    "drinking": "DRINK",
    "drank": "DRINK-PAST",
    "sleep": "SLEEP",
    "sleeping": "SLEEP",
    "slept": "SLEEP-PAST",
    "like": "LIKE",
    "likes": "LIKE",
    "liked": "LIKE-PAST",
    "want": "WANT",
    "wants": "WANT",
    "wanted": "WANT-PAST",
    "need": "NEED",
    "needs": "NEED",
    "needed": "NEED-PAST",
    
    # Common nouns
    "name": "NAME",
    "home": "HOME",
    "house": "HOUSE",
    "food": "FOOD",
    "water": "WATER",
    "school": "SCHOOL",
    "work": "WORK",
    "job": "JOB",
    "family": "FAMILY",
    "friend": "FRIEND",
    "friends": "FRIEND-PLURAL",
    "time": "TIME",
    "day": "DAY",
    "week": "WEEK",
    "month": "MONTH",
    "year": "YEAR",
    
    # Common adjectives
    "good": "GOOD",
    "bad": "BAD",
    "big": "BIG",
    "small": "SMALL",
    "hot": "HOT",
    "cold": "COLD",
    "happy": "HAPPY",
    "sad": "SAD",
    "hungry": "HUNGRY",
    "thirsty": "THIRSTY",
    "tired": "TIRED",
    "sick": "SICK",
    
    # Numbers
    "one": "ONE",
    "two": "TWO",
    "three": "THREE",
    "four": "FOUR",
    "five": "FIVE",
    "six": "SIX",
    "seven": "SEVEN",
    "eight": "EIGHT",
    "nine": "NINE",
    "ten": "TEN",
    
    # Time expressions
    "today": "TODAY",
    "tomorrow": "TOMORROW",
    "yesterday": "YESTERDAY",
    "now": "NOW",
    "later": "LATER",
    "morning": "MORNING",
    "afternoon": "AFTERNOON",
    "evening": "EVENING",
    "night": "NIGHT",
}

# Load custom translation rules if available
def load_translation_rules():
    """Load custom translation rules from the JSON file if it exists."""
    try:
        if os.path.exists(TRANSLATION_RULES_FILE):
            with open(TRANSLATION_RULES_FILE, 'r') as f:
                custom_rules = json.load(f)
            logger.info(f"Loaded {len(custom_rules)} custom translation rules")
            return custom_rules
        else:
            logger.info("No custom translation rules file found, using defaults")
    except Exception as e:
        logger.error(f"Error loading custom translation rules: {str(e)}")
    
    return {}

# Create a combined mapping with defaults and any custom rules
ENGLISH_TO_ISL_MAPPING = {**DEFAULT_ENGLISH_TO_ISL_MAPPING, **load_translation_rules()}

def convert_text_to_gloss(text):
    """
    Convert English text to Indian Sign Language gloss.
    
    Args:
        text (str): The English text to convert.
        
    Returns:
        list: A list of ISL gloss words/phrases.
    """
    try:
        if not text:
            return []
        
        # Convert to lowercase for matching
        text = text.lower()
        
        # Remove punctuation and split into words
        text = re.sub(r'[^\w\s]', '', text)
        words = text.split()
        
        # Convert each word to its ISL gloss equivalent
        gloss_words = []
        for word in words:
            if word in ENGLISH_TO_ISL_MAPPING:
                gloss_words.append(ENGLISH_TO_ISL_MAPPING[word])
            else:
                # If no direct mapping, we can either:
                # 1. Skip the word
                # 2. Use fingerspelling (for names, etc.)
                # 3. Try to find a similar word
                # For simplicity, we'll just use the original word in uppercase
                gloss_words.append(word.upper())
        
        logger.debug(f"Converted text '{text}' to gloss: {gloss_words}")
        return gloss_words
    
    except Exception as e:
        logger.error(f"Error in text-to-gloss conversion: {str(e)}")
        return []
