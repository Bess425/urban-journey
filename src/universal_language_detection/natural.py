"""Natural language detection via Unicode script analysis and character n-gram profiles."""

import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Optional


@dataclass
class DetectionResult:
    language: str
    confidence: float
    script: str


# Unicode block ranges mapped to script names
_SCRIPT_RANGES = [
    (0x0000, 0x007F, "Latin"),
    (0x0080, 0x00FF, "Latin"),
    (0x0100, 0x024F, "Latin"),
    (0x0250, 0x02AF, "Latin"),
    (0x0370, 0x03FF, "Greek"),
    (0x0400, 0x04FF, "Cyrillic"),
    (0x0500, 0x052F, "Cyrillic"),
    (0x0530, 0x058F, "Armenian"),
    (0x0590, 0x05FF, "Hebrew"),
    (0x0600, 0x06FF, "Arabic"),
    (0x0700, 0x074F, "Syriac"),
    (0x0900, 0x097F, "Devanagari"),
    (0x0980, 0x09FF, "Bengali"),
    (0x0A00, 0x0A7F, "Gurmukhi"),
    (0x0A80, 0x0AFF, "Gujarati"),
    (0x0B00, 0x0B7F, "Oriya"),
    (0x0B80, 0x0BFF, "Tamil"),
    (0x0C00, 0x0C7F, "Telugu"),
    (0x0C80, 0x0CFF, "Kannada"),
    (0x0D00, 0x0D7F, "Malayalam"),
    (0x0E00, 0x0E7F, "Thai"),
    (0x0E80, 0x0EFF, "Lao"),
    (0x0F00, 0x0FFF, "Tibetan"),
    (0x1000, 0x109F, "Myanmar"),
    (0x10A0, 0x10FF, "Georgian"),
    (0x1100, 0x11FF, "Hangul"),
    (0x1200, 0x137F, "Ethiopic"),
    (0x13A0, 0x13FF, "Cherokee"),
    (0x1680, 0x169F, "Ogham"),
    (0x16A0, 0x16FF, "Runic"),
    (0x1700, 0x171F, "Tagalog"),
    (0x1780, 0x17FF, "Khmer"),
    (0x3000, 0x303F, "CJK"),
    (0x3040, 0x309F, "Hiragana"),
    (0x30A0, 0x30FF, "Katakana"),
    (0x3100, 0x312F, "Bopomofo"),
    (0x3130, 0x318F, "Hangul"),
    (0x3400, 0x4DBF, "CJK"),
    (0x4E00, 0x9FFF, "CJK"),
    (0xAC00, 0xD7AF, "Hangul"),
    (0xF900, 0xFAFF, "CJK"),
    (0xFB00, 0xFB4F, "Latin"),
    (0xFB50, 0xFDFF, "Arabic"),
    (0xFE30, 0xFE4F, "CJK"),
    (0xFF00, 0xFFEF, "Latin"),
    (0x20000, 0x2A6DF, "CJK"),
]


def _detect_script(text: str) -> dict[str, int]:
    """Count characters per Unicode script."""
    counts: dict[str, int] = Counter()
    for ch in text:
        if ch.isspace() or not ch.isalpha():
            continue
        cp = ord(ch)
        script = "Unknown"
        for start, end, name in _SCRIPT_RANGES:
            if start <= cp <= end:
                script = name
                break
        counts[script] += 1
    return counts


# Common word lists per language (top frequent function words)
_COMMON_WORDS: dict[str, list[str]] = {
    "English": ["the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
                "for", "not", "on", "with", "he", "as", "you", "do", "at", "this",
                "but", "his", "by", "from", "they", "we", "say", "her", "she", "or"],
    "Spanish": ["de", "la", "que", "el", "en", "y", "a", "los", "del", "se",
                "las", "un", "por", "con", "no", "una", "su", "para", "es", "al",
                "lo", "como", "más", "pero", "sus", "le", "ya", "o", "fue", "este"],
    "French": ["de", "la", "le", "et", "les", "des", "en", "un", "du", "une",
               "que", "est", "qui", "au", "il", "à", "dans", "ce", "se", "sur",
               "pas", "par", "plus", "pour", "je", "son", "ne", "avec", "tout", "on"],
    "German": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich",
               "des", "auf", "für", "ist", "im", "dem", "nicht", "ein", "eine", "als",
               "auch", "es", "an", "werden", "aus", "er", "hat", "dass", "sie", "nach"],
    "Italian": ["di", "e", "il", "la", "che", "in", "è", "un", "a", "si",
                "del", "per", "i", "con", "non", "una", "le", "ho", "della", "lo",
                "al", "gli", "ha", "o", "ma", "come", "mi", "loro", "ci", "da"],
    "Portuguese": ["de", "a", "o", "que", "e", "do", "da", "em", "um", "para",
                   "é", "com", "uma", "os", "no", "se", "na", "por", "mais", "as",
                   "dos", "como", "mas", "foi", "ao", "ele", "das", "tem", "à", "seu"],
    "Dutch": ["de", "van", "en", "het", "een", "in", "is", "op", "dat", "zijn",
              "met", "voor", "te", "aan", "niet", "ook", "om", "er", "maar", "ze"],
    "Russian": ["в", "и", "не", "на", "я", "что", "тот", "быть", "он", "с",
                "а", "весь", "это", "как", "она", "по", "но", "они", "к", "у",
                "из", "за", "его", "то", "свой", "что", "мы", "так", "же", "от"],
    "Chinese": ["的", "一", "是", "在", "不", "了", "有", "和", "人", "这",
                "中", "大", "为", "上", "个", "国", "我", "以", "要", "他",
                "时", "来", "用", "们", "生", "到", "作", "地", "于", "出"],
    "Japanese": ["の", "に", "は", "を", "た", "が", "で", "て", "と", "し",
                 "れ", "さ", "ある", "いる", "も", "する", "から", "な", "こと", "として"],
    "Korean": ["이", "의", "가", "을", "는", "에", "들", "지", "와", "한",
               "하다", "그", "수", "그리고", "있다", "도", "것", "로", "서", "으로"],
    "Arabic": ["في", "من", "إلى", "على", "أن", "هذا", "هذه", "كان", "قد", "لا",
               "ما", "مع", "كل", "ولا", "عن", "يا", "إن", "لم", "لك", "له"],
}

# Script to candidate languages mapping
_SCRIPT_LANGUAGES: dict[str, list[str]] = {
    "Latin": ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Dutch"],
    "Cyrillic": ["Russian"],
    "CJK": ["Chinese", "Japanese"],
    "Hiragana": ["Japanese"],
    "Katakana": ["Japanese"],
    "Hangul": ["Korean"],
    "Arabic": ["Arabic"],
    "Hebrew": ["Hebrew"],
    "Devanagari": ["Hindi"],
    "Greek": ["Greek"],
    "Thai": ["Thai"],
}


def _score_word_match(text: str, candidates: list[str]) -> dict[str, float]:
    """Score languages by how many common words appear in the text."""
    words = set(text.lower().split())
    scores: dict[str, float] = {}
    for lang in candidates:
        word_list = _COMMON_WORDS.get(lang, [])
        if not word_list:
            scores[lang] = 0.0
            continue
        matches = sum(1 for w in word_list if w in words)
        scores[lang] = matches / len(word_list)
    return scores


class NaturalLanguageDetector:
    """Detect the natural (human) language of a text string."""

    def detect(self, text: str) -> DetectionResult:
        """Detect the language of the given text.

        Args:
            text: Input text to classify.

        Returns:
            DetectionResult with language name, confidence, and dominant script.

        Raises:
            ValueError: If text is empty.
        """
        if not text or not text.strip():
            raise ValueError("Input text must not be empty")

        script_counts = _detect_script(text)
        if not script_counts:
            return DetectionResult(language="Unknown", confidence=0.0, script="Unknown")

        dominant_script = max(script_counts, key=script_counts.__getitem__)
        total_alpha = sum(script_counts.values())
        script_confidence = script_counts[dominant_script] / total_alpha

        candidates = _SCRIPT_LANGUAGES.get(dominant_script, [])

        # Single-language scripts resolve immediately
        if len(candidates) == 1:
            return DetectionResult(
                language=candidates[0],
                confidence=round(script_confidence, 4),
                script=dominant_script,
            )

        # Multiple candidates: use word matching
        if candidates:
            word_scores = _score_word_match(text, candidates)
            if any(s > 0 for s in word_scores.values()):
                best_lang = max(word_scores, key=word_scores.__getitem__)
                best_score = word_scores[best_lang]
                total_score = sum(word_scores.values()) or 1
                word_confidence = best_score / total_score
                combined = 0.4 * script_confidence + 0.6 * word_confidence
                return DetectionResult(
                    language=best_lang,
                    confidence=round(combined, 4),
                    script=dominant_script,
                )
            # No word matches — return first candidate with script confidence
            return DetectionResult(
                language=candidates[0],
                confidence=round(script_confidence * 0.5, 4),
                script=dominant_script,
            )

        return DetectionResult(
            language=f"Unknown ({dominant_script})",
            confidence=round(script_confidence, 4),
            script=dominant_script,
        )

    def detect_all(self, text: str, top_n: int = 3) -> list[DetectionResult]:
        """Return top N language candidates sorted by confidence.

        Args:
            text: Input text to classify.
            top_n: Maximum number of results to return.

        Returns:
            List of DetectionResult sorted by descending confidence.
        """
        if not text or not text.strip():
            raise ValueError("Input text must not be empty")

        script_counts = _detect_script(text)
        if not script_counts:
            return [DetectionResult(language="Unknown", confidence=0.0, script="Unknown")]

        dominant_script = max(script_counts, key=script_counts.__getitem__)
        total_alpha = sum(script_counts.values())
        script_confidence = script_counts[dominant_script] / total_alpha

        candidates = _SCRIPT_LANGUAGES.get(dominant_script, [])
        if not candidates:
            return [DetectionResult(
                language=f"Unknown ({dominant_script})",
                confidence=round(script_confidence, 4),
                script=dominant_script,
            )]

        word_scores = _score_word_match(text, candidates)
        total_word = sum(word_scores.values()) or 1

        results = []
        for lang in candidates:
            ws = word_scores.get(lang, 0.0)
            word_conf = ws / total_word if total_word else 0.0
            combined = 0.4 * script_confidence + 0.6 * word_conf
            results.append(DetectionResult(
                language=lang,
                confidence=round(combined, 4),
                script=dominant_script,
            ))

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results[:top_n]
