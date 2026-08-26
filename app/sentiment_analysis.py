"""
Multi-Language Sentiment Analysis Engine
Combines Auto Language Detection, Translation Bridging, TextBlob, and NLTK VADER.
"""

import json
import urllib.request
import urllib.parse
import nltk
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Ensure vader_lexicon is downloaded safely
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    try:
        nltk.download('vader_lexicon', quiet=True)
    except Exception:
        pass

# Human readable language names & flags mapping
LANGUAGE_NAMES = {
    'vi': '🇻🇳 Tiếng Việt',
    'en': '🇺🇸 English',
    'zh': '🇨🇳 中文',
    'zh-CN': '🇨🇳 中文 (Giản thể)',
    'zh-TW': '🇹🇼 中文 (Phồn thể)',
    'es': '🇪🇸 Español',
    'fr': '🇫🇷 Français',
    'ja': '🇯🇵 日本語',
    'de': '🇩🇪 Deutsch',
    'ko': '🇰🇷 한국어',
    'ru': '🇷🇺 Русский',
    'it': '🇮🇹 Italiano',
    'pt': '🇵🇹 Português',
    'th': '🇹🇭 ไทย',
    'id': '🇮🇩 Bahasa Indonesia',
    'hi': '🇮🇳 हिन्दी',
    'ar': '🇸🇦 العربية',
}


def get_sentiment_analyzer():
    """Factory helper to obtain a SentimentIntensityAnalyzer instance."""
    try:
        return SentimentIntensityAnalyzer()
    except Exception:
        nltk.download('vader_lexicon', quiet=True)
        return SentimentIntensityAnalyzer()


def detect_and_translate_to_english(text):
    """
    Detects the source language and translates non-English text to English
    using the fast and reliable Google Translate endpoint.
    
    Returns:
        tuple: (english_text, detected_lang_code, is_translated)
    """
    if not text or not text.strip():
        return text, 'en', False

    clean_text = text.strip()
    
    try:
        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q=' + urllib.parse.quote(clean_text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=4) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            
        translated_parts = [part[0] for part in res_data[0] if part and part[0]]
        translated_text = ''.join(translated_parts).strip()
        detected_lang = res_data[2] if len(res_data) > 2 else 'auto'

        is_translated = (detected_lang not in ['en', 'auto']) and bool(translated_text)
        final_english_text = translated_text if is_translated else clean_text
        return final_english_text, detected_lang, is_translated

    except Exception:
        # Fallback if network or request fails
        return clean_text, 'unknown', False


def analyze_sentiment(review_text):
    """
    Analyzes sentiment of a given review text across any language.
    
    Returns a dictionary containing:
        - sentiment: 'positive', 'neutral', or 'negative'
        - positive_pct: float (0.0 - 100.0)
        - neutral_pct: float (0.0 - 100.0)
        - negative_pct: float (0.0 - 100.0)
        - polarity: float (-1.0 to 1.0)
        - subjectivity: float (0.0 to 1.0)
        - compound: float (-1.0 to 1.0)
        - tone_description: str
        - word_count: int
        - original_text: str
        - translated_text: str (if translated)
        - detected_lang_code: str
        - detected_lang_name: str
        - is_translated: bool
    """
    if not review_text or not review_text.strip():
        return {
            'sentiment': 'neutral',
            'positive_pct': 0.0,
            'neutral_pct': 100.0,
            'negative_pct': 0.0,
            'polarity': 0.0,
            'subjectivity': 0.0,
            'compound': 0.0,
            'tone_description': 'Neutral / Empty',
            'word_count': 0,
            'original_text': '',
            'translated_text': '',
            'detected_lang_code': 'en',
            'detected_lang_name': '🇺🇸 English',
            'is_translated': False
        }

    original_text = review_text.strip()

    # Step 1: Detect Language and Bridge to English
    english_text, detected_lang_code, is_translated = detect_and_translate_to_english(original_text)
    detected_lang_name = LANGUAGE_NAMES.get(detected_lang_code, f'🌐 {detected_lang_code.upper()}')

    # Step 2: TextBlob NLP Analysis
    blob = TextBlob(english_text)
    polarity_blob = float(blob.sentiment.polarity)
    subjectivity_blob = float(blob.sentiment.subjectivity)

    # Step 3: NLTK VADER Analysis
    sia = get_sentiment_analyzer()
    vader_scores = sia.polarity_scores(english_text)
    vader_compound = float(vader_scores['compound'])
    vader_pos = float(vader_scores['pos'])
    vader_neu = float(vader_scores['neu'])
    vader_neg = float(vader_scores['neg'])

    # Step 4: Hybrid Polarity Score (-1.0 to 1.0)
    hybrid_polarity = round((polarity_blob + vader_compound) / 2.0, 3)

    # Step 5: Percentage Probabilities Calculation
    tb_pos = max(0.0, polarity_blob)
    tb_neg = max(0.0, -polarity_blob)
    tb_neu = 1.0 - (tb_pos + tb_neg)

    raw_pos = (vader_pos * 0.6) + (tb_pos * 0.4)
    raw_neg = (vader_neg * 0.6) + (tb_neg * 0.4)
    raw_neu = (vader_neu * 0.6) + (tb_neu * 0.4)

    if hybrid_polarity > 0.1:
        raw_pos += (hybrid_polarity * 0.45)
    elif hybrid_polarity < -0.1:
        raw_neg += (abs(hybrid_polarity) * 0.45)

    total_weight = raw_pos + raw_neu + raw_neg
    if total_weight <= 0:
        pos_pct, neu_pct, neg_pct = 0.0, 100.0, 0.0
    else:
        pos_pct = round((raw_pos / total_weight) * 100.0, 1)
        neg_pct = round((raw_neg / total_weight) * 100.0, 1)
        neu_pct = round(max(0.0, 100.0 - pos_pct - neg_pct), 1)

    # Step 6: Sentiment Classification
    if hybrid_polarity >= 0.15 or (pos_pct > 50 and pos_pct > neg_pct):
        sentiment = 'positive'
    elif hybrid_polarity <= -0.15 or (neg_pct > 50 and neg_pct > pos_pct):
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    # Step 7: Tone description
    if hybrid_polarity >= 0.6:
        tone_description = 'Highly Enthusiastic & Positive'
    elif hybrid_polarity >= 0.2:
        tone_description = 'Generally Favorable / Positive'
    elif hybrid_polarity <= -0.6:
        tone_description = 'Extremely Critical & Negative'
    elif hybrid_polarity <= -0.2:
        tone_description = 'Generally Unfavorable / Negative'
    else:
        tone_description = 'Balanced / Neutral'

    word_count = len(original_text.split())

    return {
        'sentiment': sentiment,
        'positive_pct': pos_pct,
        'neutral_pct': neu_pct,
        'negative_pct': neg_pct,
        'polarity': hybrid_polarity,
        'subjectivity': round(subjectivity_blob, 3),
        'compound': round(vader_compound, 3),
        'tone_description': tone_description,
        'word_count': word_count,
        'original_text': original_text,
        'translated_text': english_text if is_translated else '',
        'detected_lang_code': detected_lang_code,
        'detected_lang_name': detected_lang_name,
        'is_translated': is_translated
    }
