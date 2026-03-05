"""Universal Language Detection - detect both natural and programming languages."""

from .detector import UniversalDetector
from .natural import NaturalLanguageDetector
from .programming import ProgrammingLanguageDetector

__version__ = "1.0.0"
__all__ = ["UniversalDetector", "NaturalLanguageDetector", "ProgrammingLanguageDetector"]
