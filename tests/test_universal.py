"""Tests for UniversalDetector."""

import pytest
from universal_language_detection import UniversalDetector


@pytest.fixture
def detector():
    return UniversalDetector()


class TestDetect:
    def test_english_prose(self, detector):
        result = detector.detect(
            "The quick brown fox jumps over the lazy dog. "
            "It was a bright cold day in April."
        )
        assert result.kind == "natural"
        assert result.language == "English"

    def test_python_code(self, detector):
        result = detector.detect(
            "def greet(name):\n    print(f'Hello, {name}!')\n\ngreet('World')"
        )
        assert result.kind == "programming"
        assert result.language == "Python"

    def test_javascript_code(self, detector):
        result = detector.detect(
            "const x = 42;\nconst greet = (name) => console.log(`Hi ${name}`);\ngreet('World');"
        )
        assert result.kind == "programming"
        assert result.language == "JavaScript"

    def test_html_detected_as_programming(self, detector):
        result = detector.detect("<!DOCTYPE html><html><body><h1>Hello</h1></body></html>")
        assert result.kind == "programming"
        assert result.language == "HTML"

    def test_sql_detected_as_programming(self, detector):
        result = detector.detect(
            "SELECT id, name FROM users WHERE active = 1 ORDER BY name;"
        )
        assert result.kind == "programming"
        assert result.language == "SQL"

    def test_russian_text(self, detector):
        result = detector.detect("Привет мир, это тест на русском языке для проверки")
        assert result.kind == "natural"
        assert result.script == "Cyrillic"

    def test_result_confidence_in_range(self, detector):
        result = detector.detect("Hello world, this is English text")
        assert 0.0 <= result.confidence <= 1.0

    def test_empty_raises(self, detector):
        with pytest.raises(ValueError):
            detector.detect("")

    def test_programming_result_has_features(self, detector):
        result = detector.detect(
            "import java.util.List;\npublic class Foo { public static void main(String[] args) {} }"
        )
        assert result.kind == "programming"
        assert isinstance(result.matched_features, list)

    def test_natural_result_has_script(self, detector):
        result = detector.detect("The dog sat on the mat by the door")
        assert result.kind == "natural"
        assert result.script is not None


class TestDetectNatural:
    def test_returns_ranked_list(self, detector):
        results = detector.detect_natural("Hello the quick fox jumps over a lazy dog")
        assert len(results) >= 1
        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)


class TestDetectProgramming:
    def test_returns_ranked_list(self, detector):
        results = detector.detect_programming(
            "def foo(x):\n    return x * 2\n\nprint(foo(3))"
        )
        assert len(results) >= 1
        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)
