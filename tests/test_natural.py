"""Tests for natural language detection."""

import pytest
from universal_language_detection import NaturalLanguageDetector


@pytest.fixture
def detector():
    return NaturalLanguageDetector()


class TestDetect:
    def test_english(self, detector):
        result = detector.detect("The quick brown fox jumps over the lazy dog")
        assert result.language == "English"
        assert result.confidence > 0

    def test_spanish(self, detector):
        result = detector.detect("El rápido zorro marrón salta sobre el perro perezoso")
        assert result.language == "Spanish"
        assert result.confidence > 0

    def test_french(self, detector):
        result = detector.detect(
            "Je ne suis pas dans cette ville mais il est avec nous sur le pont"
        )
        assert result.language == "French"
        assert result.confidence > 0

    def test_german(self, detector):
        result = detector.detect("Der schnelle braune Fuchs springt über den faulen Hund")
        assert result.language == "German"
        assert result.confidence > 0

    def test_russian_script(self, detector):
        result = detector.detect("Привет мир, это тест на русском языке")
        assert result.language == "Russian"
        assert result.script == "Cyrillic"

    def test_chinese_script(self, detector):
        result = detector.detect("这是一个中文测试句子，用于检测语言")
        assert result.script == "CJK"
        assert result.confidence > 0

    def test_arabic_script(self, detector):
        result = detector.detect("مرحبا بالعالم هذا اختبار باللغة العربية")
        assert result.script == "Arabic"
        assert result.confidence > 0

    def test_empty_raises(self, detector):
        with pytest.raises(ValueError):
            detector.detect("")

    def test_whitespace_only_raises(self, detector):
        with pytest.raises(ValueError):
            detector.detect("   \n\t  ")

    def test_result_has_confidence(self, detector):
        result = detector.detect("Hello world this is a test")
        assert 0.0 <= result.confidence <= 1.0

    def test_result_has_script(self, detector):
        result = detector.detect("Hello world")
        assert result.script is not None


class TestDetectAll:
    def test_returns_list(self, detector):
        results = detector.detect_all("Hello world, the quick fox")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_sorted_by_confidence(self, detector):
        results = detector.detect_all("Hello world the quick brown fox")
        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)

    def test_top_n_respected(self, detector):
        results = detector.detect_all("Hello world", top_n=2)
        assert len(results) <= 2

    def test_empty_raises(self, detector):
        with pytest.raises(ValueError):
            detector.detect_all("")
