autodidactes"""UniversalDetector: single entry point for both natural and programming language detection."""

from dataclasses import dataclass, field
from typing import Optional

from .natural import NaturalLanguageDetector, DetectionResult as NaturalResult
from .programming import ProgrammingLanguageDetector, ProgrammingDetectionResult


@dataclass
class UniversalResult:
    """Result returned by UniversalDetector."""

    kind: str               # "natural" | "programming" | "unknown"
    language: str
    confidence: float
    script: Optional[str] = None                    # Only for natural language
    matched_features: list[str] = field(default_factory=list)  # Only for programming


_CODE_INDICATORS = [
    # Strong signals that this is source code, not prose
    r'^\s*#!',                      # shebang
    r'<\?php',                      # PHP open tag
    r'<!DOCTYPE',                   # HTML
    r'^\s*import\s+',               # import statement
    r'^\s*#include\s*',             # C/C++ include
    r'\bdef\s+\w+\s*\(',            # Python def
    r'\bfunc\s+\w+',                # Go/Swift func
    r'\bfunction\s+\w+',            # JS/PHP function
    r'\bpublic\s+class\b',          # Java
    r'^\s*SELECT\b',                # SQL
    r'\bpackage\s+\w+\s*;',         # Java package
    r'\bpackage\s+main\b',          # Go
    r'\bconst\s+\w+\s*=',           # JS/TS const assignment
    r'\blet\s+\w+\s*=',             # JS/TS let assignment
    r'=>\s*[\{(\w]',                # JS/TS arrow function
    r'\bconsole\.\w+\s*\(',         # JS console.*()
    r'\bprintln?\s*!\s*\(',         # Rust println!/print!
    r'\bfmt\.\w+\(',                # Go fmt.*()
    r'\b(val|var)\s+\w+\s*[:=]',   # Kotlin/Swift val/var
    r'\bfn\s+\w+\s*\(',             # Rust fn
]

import re as _re
_CODE_PATTERN = _re.compile(
    "|".join(_CODE_INDICATORS), _re.IGNORECASE | _re.MULTILINE
)


class UniversalDetector:
    """Detect whether text is natural language or source code, and identify which one.

    Usage::

        detector = UniversalDetector()

        result = detector.detect("Hello, how are you?")
        # UniversalResult(kind='natural', language='English', confidence=0.87, ...)

        result = detector.detect("def foo(x):\\n    return x * 2")
        # UniversalResult(kind='programming', language='Python', confidence=0.91, ...)
    """

    def __init__(self) -> None:
        self._natural = NaturalLanguageDetector()
        self._programming = ProgrammingLanguageDetector()

    def detect(self, text: str) -> UniversalResult:
        """Auto-detect whether the text is natural language or source code.

        The method first checks for code-specific syntactic markers. If strong
        signals are found it runs programming detection; otherwise it runs natural
        language detection and falls back to programming detection when the natural
        confidence is low.

        Args:
            text: Any text or code snippet.

        Returns:
            UniversalResult describing the kind and detected language.

        Raises:
            ValueError: If text is empty.
        """
        if not text or not text.strip():
            raise ValueError("Input text must not be empty")

        is_code = bool(_CODE_PATTERN.search(text))

        if is_code:
            prog_result = self._programming.detect(text)
            if prog_result.confidence > 0.05:
                return UniversalResult(
                    kind="programming",
                    language=prog_result.language,
                    confidence=prog_result.confidence,
                    matched_features=prog_result.matched_features,
                )

        # Try natural language first
        nat_result = self._natural.detect(text)
        if nat_result.confidence >= 0.3:
            return UniversalResult(
                kind="natural",
                language=nat_result.language,
                confidence=nat_result.confidence,
                script=nat_result.script,
            )

        # Fall back to programming detection
        prog_result = self._programming.detect(text)
        if prog_result.confidence > 0.05:
            return UniversalResult(
                kind="programming",
                language=prog_result.language,
                confidence=prog_result.confidence,
                matched_features=prog_result.matched_features,
            )

        return UniversalResult(kind="unknown", language="Unknown", confidence=0.0)

    def detect_natural(self, text: str, top_n: int = 3) -> list[NaturalResult]:
        """Detect natural language candidates explicitly.

        Args:
            text: Natural language text.
            top_n: Number of results to return.

        Returns:
            Ranked list of NaturalResult.
        """
        return self._natural.detect_all(text, top_n=top_n)

    def detect_programming(self, text: str, top_n: int = 3) -> list[ProgrammingDetectionResult]:
        """Detect programming language candidates explicitly.

        Args:
            text: Source code snippet.
            top_n: Number of results to return.

        Returns:
            Ranked list of ProgrammingDetectionResult.
        """
        return self._programming.detect_all(text, top_n=top_n)
