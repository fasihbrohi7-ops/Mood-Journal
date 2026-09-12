import re
import vaderSentiment.vaderSentiment as vs
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Comprehensive Roman Urdu sentiment lexicon
ROMAN_URDU_LEXICON = {
    # Highly positive (+2.5 to +3.5)
    'zabardast': 3.4, 'zbrdst': 3.4, 'behtareen': 3.3, 'behtreen': 3.3, 'shaandar': 3.2,
    'shandar': 3.2, 'kamaal': 3.0, 'kamal': 3.0, 'lajawab': 3.2, 'khushgawar': 2.8,
    'alhamdulillah': 2.8, 'mashallah': 2.8, 'sukoon': 2.8, 'sukun': 2.8, 'kamyab': 2.7,
    'kamiyab': 2.7, 'kamyabi': 2.8, 'kamiyabi': 2.8, 'pyara': 2.5, 'pyari': 2.5,
    'pyaara': 2.5, 'muhabbat': 2.7, 'mohabbat': 2.7, 'pyaar': 2.5, 'pyar': 2.5,
    'mubarak': 2.4, 'farmaa': 2.0, 'shukrana': 2.5,

    # Positive (+1.5 to +2.4)
    'acha': 2.0, 'achha': 2.0, 'achi': 2.0, 'achhi': 2.0, 'ache': 2.0, 'achhe': 2.0,
    'achay': 2.0, 'khush': 2.2, 'khushi': 2.2, 'theek': 1.6, 'thik': 1.6,
    'maza': 2.1, 'mazay': 2.1, 'mazedar': 2.3, 'lazeez': 2.2, 'lutf': 2.0,
    'umeed': 1.8, 'shukr': 2.2, 'faida': 1.6, 'fayeda': 1.6, 'chain': 2.0,
    'rahat': 2.2, 'itminan': 2.2, 'itmeenan': 2.2, 'haseen': 2.4, 'mast': 2.4,
    'fit': 2.0, 'umda': 2.2, 'behtar': 1.8, 'khoob': 2.2, 'khoobsurat': 2.5,
    'roshan': 2.0, 'khushhaal': 2.4,

    # Mild Negative (-1.0 to -1.9)
    'thak': -1.6, 'thaka': -1.6, 'thaki': -1.6, 'thakan': -1.7, 'mushkil': -1.5,
    'masla': -1.6, 'maslay': -1.6, 'tang': -1.8, 'boring': -1.5, 'kamzor': -1.4,
    'beemar': -1.8, 'bimar': -1.8, 'bimaar': -1.8, 'sust': -1.4, 'susti': -1.5,
    'ghabrahat': -1.7, 'khali': -1.0,

    # Negative (-2.0 to -2.7)
    'bura': -2.3, 'buri': -2.3, 'bure': -2.3, 'buray': -2.3, 'kharab': -2.5,
    'kharaab': -2.5, 'udaas': -2.6, 'udas': -2.6, 'gham': -2.4, 'ghamgeen': -2.6,
    'dard': -2.2, 'dukh': -2.4, 'ghussa': -2.4, 'gussa': -2.4, 'tension': -2.3,
    'pareshaan': -2.4, 'pareshan': -2.4, 'parayshan': -2.4, 'pareshani': -2.5,
    'afsos': -2.2, 'takleef': -2.5, 'taklif': -2.5, 'nuksan': -2.2, 'nuksaan': -2.2,
    'khof': -2.3, 'dar': -2.0, 'mayoos': -2.4, 'mayoosi': -2.5, 'sharminda': -2.1,
    'ruswa': -2.5, 'rona': -2.0, 'ro': -2.0,

    # Highly Negative (-2.8 to -3.5)
    'barbaad': -3.4, 'barbad': -3.4, 'tabah': -3.3, 'zillat': -3.2, 'nafrat': -3.2,
    'musibat': -3.0, 'moseebat': -3.0, 'laachar': -2.8, 'maut': -3.3, 'halakat': -3.2
}

ROMAN_URDU_BOOSTERS = {
    'bohot': 0.293, 'boht': 0.293, 'bht': 0.293, 'intehai': 0.35, 'nihayat': 0.3,
    'sakht': 0.3, 'kafi': 0.25, 'kaafi': 0.25, 'hadd': 0.293, 'zyada': 0.25,
    'ziada': 0.25, 'bilkul': 0.293,
    'thoda': -0.25, 'thodi': -0.25, 'thora': -0.25, 'thori': -0.25, 'kam': -0.2,
    'halka': -0.2, 'halki': -0.2, 'zara': -0.2
}

ROMAN_URDU_NEGATIONS = ['nahi', 'nahin', 'ni', 'na', 'mat']

ROMAN_URDU_STOP_MARKERS = {
    'aaj', 'tha', 'thi', 'the', 'hai', 'hain', 'mein', 'me', 'ka', 'ki', 'ke',
    'ko', 'se', 'par', 'pe', 'kya', 'kyun', 'kuch', 'bhi', 'ab', 'gaya', 'gayi',
    'gaye', 'raha', 'rahi', 'rahe', 'hoga', 'hogi', 'karna', 'kiya', 'karenge',
    'subah', 'shaam', 'raat', 'din', 'dost', 'log', 'hum', 'main', 'tum', 'aap'
}

# Initialize VADER Analyzer with extended Roman Urdu lexicon
_analyzer = SentimentIntensityAnalyzer()
_analyzer.lexicon.update(ROMAN_URDU_LEXICON)
vs.BOOSTER_DICT.update(ROMAN_URDU_BOOSTERS)
for _neg in ROMAN_URDU_NEGATIONS:
    if _neg not in vs.NEGATE:
        vs.NEGATE.append(_neg)

def preprocess_text(text: str) -> str:
    # 1. Normalize post-word negation: e.g. 'acha nahi' -> 'nahi acha'
    # Also handles 'acha din nahi' -> 'nahi acha din'
    pattern = r'\b([a-zA-Z]+)(?:\s+(din|baat|waqt|kaam|cheez|din))?\s+(nahi|nahin|ni|na)\b'
    def _neg_repl(m):
        adj = m.group(1)
        noun = m.group(2)
        neg = m.group(3)
        if noun:
            return f'{neg} {adj} {noun}'
        return f'{neg} {adj}'

    normalized = re.sub(pattern, _neg_repl, text, flags=re.IGNORECASE)

    # 2. Map Roman Urdu contrastive conjunctions ('lekin', 'magar') to 'but' for VADER clause weighting
    normalized = re.sub(r'\b(lekin|magar|laikin|par|halaankay|halankay)\b', 'but', normalized, flags=re.IGNORECASE)
    return normalized

def detect_language(text: str) -> str:
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    if not words:
        return 'English'
    
    urdu_matches = sum(1 for w in words if w in ROMAN_URDU_LEXICON or w in ROMAN_URDU_BOOSTERS or w in ROMAN_URDU_STOP_MARKERS or w in ROMAN_URDU_NEGATIONS)
    ratio = urdu_matches / len(words)
    
    if ratio >= 0.3:
        return 'Roman Urdu'
    elif ratio > 0.1:
        return 'Mixed (English & Urdu)'
    return 'English'

def get_mood_bucket(score: float) -> str:
    if score < -0.5:
        return 'very_negative'
    elif score < -0.1:
        return 'negative'
    elif score <= 0.1:
        return 'neutral'
    elif score <= 0.5:
        return 'positive'
    else:
        return 'very_positive'

def analyze_sentiment(text: str) -> dict:
    processed = preprocess_text(text)
    polarity = _analyzer.polarity_scores(processed)['compound']
    score = round(float(polarity), 2)
    bucket = get_mood_bucket(score)
    lang = detect_language(text)
    return {
        'score': score,
        'bucket': bucket,
        'language': lang
    }
