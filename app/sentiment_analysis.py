"""
Multi-Language Sentiment Analysis Engine
Combines Auto Language Detection, Multi-Source Translation, Native Vietnamese Lexicon, TextBlob, and NLTK VADER.
"""

import re
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

# Character sets for instant offline language detection
VIETNAMESE_CHARS = set('àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ')

LANGUAGE_NAMES = {
    'vi': '🇻🇳 Tiếng Việt',
    'en': '🇺🇸 English',
    'zh': '🇨🇳 中文',
    'zh-CN': '🇨🇳 中文',
    'ja': '🇯🇵 日本語',
    'ko': '🇰🇷 한국어',
    'es': '🇪🇸 Español',
    'fr': '🇫🇷 Français',
    'de': '🇩🇪 Deutsch',
    'ru': '🇷🇺 Русский',
}

MYMEMORY_LANG_MAP = {
    'zh': 'zh-CN',
    'vi': 'vi',
    'ja': 'ja',
    'ko': 'ko',
    'es': 'es',
    'fr': 'fr',
    'de': 'de',
    'ru': 'ru',
}

# Rich Vietnamese Sentiment Dictionary (Keywords + Weights)
VI_POSITIVE_WORDS = {
    'tuyệt vời': 2.0, 'xuất sắc': 2.0, 'đỉnh cao': 2.0, 'siêu phẩm': 2.0, 'tuyệt phẩm': 2.0,
    'mãn nhãn': 1.8, 'kinh điển': 1.8, 'hoàn hảo': 1.8, 'rất hay': 1.6, 'cảm động': 1.6,
    'ấn tượng': 1.5, 'hấp dẫn': 1.5, 'cuốn hút': 1.5, 'đáng xem': 1.5, 'bùng nổ': 1.5,
    'xuất thần': 1.5, 'lôi cuốn': 1.5, 'chất lượng': 1.4, 'thích': 1.2, 'đẹp': 1.2,
    'hay': 1.2, 'tốt': 1.2, 'khen': 1.2, 'thành công': 1.3, 'sâu sắc': 1.4,
    'thú vị': 1.2, 'nghẹn ngào': 1.4, 'đáng tiền': 1.5, 'mê': 1.3, 'nghẹt thở': 1.2,
    'bất ngờ': 1.1, 'sáng tạo': 1.3, 'tuyệt': 1.4, 'hài lòng': 1.3, 'đỉnh': 1.5
}

VI_NEGATIVE_WORDS = {
    'thất vọng': -2.0, 'thảm họa': -2.0, 'dở tệ': -2.0, 'tệ hại': -2.0, 'nhảm nhí': -1.9,
    'phí tiền': -1.8, 'lãng phí': -1.7, 'tiếc tiền': -1.7, 'phí thời gian': -1.8,
    'nhạt nhẽo': -1.6, 'buồn ngủ': -1.5, 'rời rạc': -1.5, 'ức chế': -1.6, 'bực mình': -1.5,
    'lỗ hổng': -1.4, 'dở': -1.5, 'tệ': -1.5, 'chán': -1.4, 'nhảm': -1.5, 'xấu': -1.3,
    'không hay': -1.5, 'vớ vẩn': -1.5, 'gượng gạo': -1.4, 'nhạt': -1.2, 'dài dòng': -1.2,
    'chán ngắt': -1.6, 'nực cười': -1.3, 'đáng tiếc': -1.0, 'dở hơi': -1.4, 'thất bại': -1.6,
    'kém': -1.3, 'tệ bạc': -1.6, 'nhức đầu': -1.4, 'khó chịu': -1.4
}

VI_INTENSIFIERS = {'rất': 1.4, 'cực kỳ': 1.6, 'quá': 1.3, 'vô cùng': 1.6, 'siêu': 1.5, 'hết sức': 1.5}
VI_NEGATORS = {'không': -1.0, 'chẳng': -1.0, 'chưa': -0.8, 'không hề': -1.2, 'kém': -0.8}


def get_sentiment_analyzer():
    """Factory helper to obtain a SentimentIntensityAnalyzer instance."""
    try:
        return SentimentIntensityAnalyzer()
    except Exception:
        nltk.download('vader_lexicon', quiet=True)
        return SentimentIntensityAnalyzer()


def detect_language(text):
    """
    Accurately detects source language using character signatures.
    """
    if not text:
        return 'en', '🇺🇸 English'

    t_lower = text.lower()

    # 1. Check Vietnamese
    if any(c in VIETNAMESE_CHARS for c in t_lower):
        return 'vi', '🇻🇳 Tiếng Việt'

    # 2. Check Japanese (Hiragana or Katakana)
    if re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
        return 'ja', '🇯🇵 日本語'

    # 3. Check Korean (Hangul)
    if re.search(r'[\uac00-\ud7af]', text):
        return 'ko', '🇰🇷 한국어'

    # 4. Check Chinese (Hanzi)
    if re.search(r'[\u4e00-\u9fff]', text):
        return 'zh', '🇨🇳 中文'

    # 5. Check Russian (Cyrillic)
    if re.search(r'[\u0400-\u04ff]', text):
        return 'ru', '🇷🇺 Русский'

    return 'en', '🇺🇸 English'


def translate_text_resilient(text, src_lang='auto'):
    """
    Translates non-English text to English with multi-source fallback (MyMemory & Google).
    """
    if not text or src_lang == 'en':
        return text, False

    clean_text = text.strip()
    mapped_lang = MYMEMORY_LANG_MAP.get(src_lang, src_lang if src_lang != 'auto' else 'Autodetect')

    # Strategy 1: MyMemory API (Fast, Free, No rate-limit issues for basic text)
    try:
        lang_pair = f'{mapped_lang}|en'
        url = f'https://api.mymemory.translated.net/get?q={urllib.parse.quote(clean_text)}&langpair={lang_pair}'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        trans_res = data.get('responseData', {}).get('translatedText', '')
        if trans_res and not trans_res.startswith('MYMEMORY WARNING') and trans_res.strip() != clean_text:
            return trans_res.strip(), True
    except Exception:
        pass

    # Strategy 2: Google Translate API fallback
    try:
        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q=' + urllib.parse.quote(clean_text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
        translated_parts = [part[0] for part in res_data[0] if part and part[0]]
        trans_res = ''.join(translated_parts).strip()
        if trans_res and trans_res != clean_text:
            return trans_res, True
    except Exception:
        pass

    return clean_text, False


def calculate_vietnamese_lexicon_score(text):
    """
    Calculates native Vietnamese sentiment polarity using dictionary and rules.
    """
    t_lower = text.lower()
    score = 0.0
    pos_matches = 0
    neg_matches = 0

    # Match multi-word phrases and single words
    for word, weight in VI_POSITIVE_WORDS.items():
        if word in t_lower:
            score += weight
            pos_matches += 1

    for word, weight in VI_NEGATIVE_WORDS.items():
        if word in t_lower:
            score += weight
            neg_matches += 1

    # Check for negations ("không hay", "chẳng thích")
    for neg in VI_NEGATORS:
        if neg in t_lower:
            score *= 0.6

    if pos_matches + neg_matches > 0:
        # Normalize to -1.0 to 1.0 range
        normalized_polarity = max(-1.0, min(1.0, score / max(1.0, (pos_matches + neg_matches) * 1.5)))
        return round(normalized_polarity, 3), pos_matches, neg_matches

    return 0.0, 0, 0


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

    # Step 1: Detect Language (Instant & 100% Reliable)
    detected_lang_code, detected_lang_name = detect_language(original_text)

    # Step 2: Native Vietnamese Lexicon Check (if Vietnamese)
    vi_polarity, vi_pos_count, vi_neg_count = (0.0, 0, 0)
    if detected_lang_code == 'vi':
        vi_polarity, vi_pos_count, vi_neg_count = calculate_vietnamese_lexicon_score(original_text)

    # Step 3: Multi-Source Translation to English
    english_text, is_translated = translate_text_resilient(original_text, src_lang=detected_lang_code)

    # Step 4: TextBlob NLP
    blob = TextBlob(english_text)
    polarity_blob = float(blob.sentiment.polarity)
    subjectivity_blob = float(blob.sentiment.subjectivity)

    # Step 5: NLTK VADER
    sia = get_sentiment_analyzer()
    vader_scores = sia.polarity_scores(english_text)
    vader_compound = float(vader_scores['compound'])
    vader_pos = float(vader_scores['pos'])
    vader_neu = float(vader_scores['neu'])
    vader_neg = float(vader_scores['neg'])

    # Step 6: Hybrid Polarity Blend
    if detected_lang_code == 'vi' and (vi_pos_count > 0 or vi_neg_count > 0):
        if is_translated:
            hybrid_polarity = round((vi_polarity * 0.45) + (polarity_blob * 0.25) + (vader_compound * 0.3), 3)
        else:
            hybrid_polarity = vi_polarity
            vader_compound = vi_polarity
            polarity_blob = vi_polarity
    else:
        hybrid_polarity = round((polarity_blob + vader_compound) / 2.0, 3)

    # Step 7: Calculate Percentage Probabilities
    tb_pos = max(0.0, polarity_blob)
    tb_neg = max(0.0, -polarity_blob)
    tb_neu = max(0.0, 1.0 - (tb_pos + tb_neg))

    if detected_lang_code == 'vi' and not is_translated and (vi_pos_count > 0 or vi_neg_count > 0):
        if vi_polarity > 0:
            raw_pos = 0.55 + (vi_polarity * 0.45)
            raw_neg = 0.05
            raw_neu = max(0.0, 1.0 - raw_pos - raw_neg)
        else:
            raw_neg = 0.55 + (abs(vi_polarity) * 0.45)
            raw_pos = 0.05
            raw_neu = max(0.0, 1.0 - raw_pos - raw_neg)
    else:
        raw_pos = (vader_pos * 0.55) + (tb_pos * 0.45)
        raw_neg = (vader_neg * 0.55) + (tb_neg * 0.45)
        raw_neu = (vader_neu * 0.55) + (tb_neu * 0.45)

        if hybrid_polarity > 0.1:
            raw_pos += (hybrid_polarity * 0.5)
        elif hybrid_polarity < -0.1:
            raw_neg += (abs(hybrid_polarity) * 0.5)

    total_weight = raw_pos + raw_neu + raw_neg
    if total_weight <= 0:
        pos_pct, neu_pct, neg_pct = 0.0, 100.0, 0.0
    else:
        pos_pct = round((raw_pos / total_weight) * 100.0, 1)
        neg_pct = round((raw_neg / total_weight) * 100.0, 1)
        neu_pct = round(max(0.0, 100.0 - pos_pct - neg_pct), 1)

    # Step 8: Sentiment Classification
    if hybrid_polarity >= 0.12 or (pos_pct > 45 and pos_pct > neg_pct):
        sentiment = 'positive'
    elif hybrid_polarity <= -0.12 or (neg_pct > 45 and neg_pct > pos_pct):
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    # Step 9: Tone Description
    if hybrid_polarity >= 0.5:
        tone_description = 'Highly Enthusiastic & Positive'
    elif hybrid_polarity >= 0.12:
        tone_description = 'Generally Favorable / Positive'
    elif hybrid_polarity <= -0.5:
        tone_description = 'Extremely Critical & Negative'
    elif hybrid_polarity <= -0.12:
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
        'subjectivity': round(subjectivity_blob if subjectivity_blob > 0 else (0.75 if sentiment != 'neutral' else 0.2), 3),
        'compound': round(vader_compound, 3),
        'tone_description': tone_description,
        'word_count': word_count,
        'original_text': original_text,
        'translated_text': english_text if is_translated else '',
        'detected_lang_code': detected_lang_code,
        'detected_lang_name': detected_lang_name,
        'is_translated': is_translated
    }
