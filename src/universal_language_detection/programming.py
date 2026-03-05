"""Programming language detection via syntax pattern analysis."""

import re
from dataclasses import dataclass, field


@dataclass
class ProgrammingDetectionResult:
    language: str
    confidence: float
    matched_features: list[str] = field(default_factory=list)


# Each rule: (feature_name, compiled_regex, weight)
_RULES: dict[str, list[tuple[str, re.Pattern, float]]] = {
    "Python": [
        ("def keyword",      re.compile(r'\bdef\s+\w+\s*\('),          2.0),
        ("import statement", re.compile(r'\bimport\s+\w+|\bfrom\s+\w+\s+import\b'), 1.5),
        ("class keyword",    re.compile(r'\bclass\s+\w+[\s:(]'),        1.5),
        ("print function",   re.compile(r'\bprint\s*\('),               1.0),
        ("elif keyword",     re.compile(r'\belif\b'),                   2.0),
        ("f-string",         re.compile(r'f["\'].*?\{.*?\}.*?["\']'),   2.0),
        ("lambda keyword",   re.compile(r'\blambda\b'),                 1.5),
        ("self parameter",   re.compile(r'\bself\b'),                   1.5),
        ("None/True/False",  re.compile(r'\bNone\b|\bTrue\b|\bFalse\b'), 1.5),
        ("type hints",       re.compile(r'\bdef\s+\w+\(.*?:\s*\w+'),   1.0),
        ("list comprehension", re.compile(r'\[.+\bfor\b.+\bin\b'),      2.0),
        ("decorator",        re.compile(r'^\s*@\w+', re.MULTILINE),     2.0),
        ("indented colon",   re.compile(r':\s*\n\s+\S'),               0.5),
        ("triple quote",     re.compile(r'"""[\s\S]*?"""'),             1.5),
    ],
    "JavaScript": [
        ("const/let/var",    re.compile(r'\b(const|let|var)\s+\w+'),    2.0),
        ("function keyword", re.compile(r'\bfunction\s*\w*\s*\('),      1.5),
        ("arrow function",   re.compile(r'=>\s*[\{(]|=>\s*\w'),         2.0),
        ("console.log",      re.compile(r'\bconsole\.\w+\s*\('),        2.0),
        ("require/import",   re.compile(r'\brequire\s*\(|import\s+.+\bfrom\b'), 1.5),
        ("=== operator",     re.compile(r'===|!=='),                    2.0),
        ("undefined/null",   re.compile(r'\bundefined\b|\bnull\b'),      1.0),
        ("async/await",      re.compile(r'\basync\b|\bawait\b'),        1.5),
        ("template literal", re.compile(r'`[^`]*\$\{'),                 2.0),
        ("typeof",           re.compile(r'\btypeof\b'),                 1.5),
        ("prototype",        re.compile(r'\.prototype\b'),              1.5),
        ("document/window",  re.compile(r'\bdocument\b|\bwindow\b'),    1.5),
    ],
    "TypeScript": [
        ("type annotation",  re.compile(r':\s*(string|number|boolean|any|void|never|unknown)\b'), 2.5),
        ("interface keyword",re.compile(r'\binterface\s+\w+'),          2.5),
        ("type keyword",     re.compile(r'\btype\s+\w+\s*='),           2.5),
        ("enum keyword",     re.compile(r'\benum\s+\w+'),               2.5),
        ("generic syntax",   re.compile(r'<\w+>|Array<|Promise<|Record<'), 1.5),
        ("const/let/var",    re.compile(r'\b(const|let|var)\s+\w+'),    1.0),
        ("access modifier",  re.compile(r'\b(public|private|protected|readonly)\s+\w+'), 2.0),
        ("as keyword",       re.compile(r'\bas\s+\w+'),                 1.0),
        ("implements",       re.compile(r'\bimplements\s+\w+'),         2.0),
        ("import type",      re.compile(r'import\s+type\s'),            2.5),
    ],
    "Java": [
        ("public class",     re.compile(r'\bpublic\s+class\s+\w+'),     2.5),
        ("main method",      re.compile(r'public\s+static\s+void\s+main'), 3.0),
        ("System.out",       re.compile(r'\bSystem\.out\.'),            2.0),
        ("import java",      re.compile(r'\bimport\s+java\.\w+'),       3.0),
        ("new keyword",      re.compile(r'\bnew\s+\w+\s*\('),           1.0),
        ("@Override",        re.compile(r'@Override'),                  2.5),
        ("void return type", re.compile(r'\bvoid\s+\w+\s*\('),          1.5),
        ("final keyword",    re.compile(r'\bfinal\s+\w+'),              1.5),
        ("throws",           re.compile(r'\bthrows\s+\w+'),             2.0),
        ("extends/implements", re.compile(r'\bextends\s+\w+|\bimplements\s+\w+'), 2.0),
    ],
    "C": [
        ("#include",         re.compile(r'#include\s*[<"]'),            2.5),
        ("#define",          re.compile(r'#define\s+\w+'),              2.0),
        ("printf",           re.compile(r'\bprintf\s*\('),              2.0),
        ("main function",    re.compile(r'\bint\s+main\s*\('),          3.0),
        ("pointer",          re.compile(r'\w+\s*\*\s*\w+|\*\w+\s*='),  1.5),
        ("malloc/free",      re.compile(r'\bmalloc\s*\(|\bfree\s*\('), 2.5),
        ("struct keyword",   re.compile(r'\bstruct\s+\w+'),             2.0),
        ("typedef",          re.compile(r'\btypedef\b'),                2.0),
        ("C types",          re.compile(r'\b(int|char|float|double|void|long|short|unsigned)\s+\w+'), 1.0),
        ("arrow operator",   re.compile(r'\w+\s*->\s*\w+'),             1.5),
    ],
    "C++": [
        ("#include",         re.compile(r'#include\s*[<"]'),            1.5),
        ("cout/cin",         re.compile(r'\b(cout|cin)\s*<<|>>\s*(cout|cin)'), 3.0),
        ("namespace",        re.compile(r'\bnamespace\s+\w+|\busing\s+namespace'), 3.0),
        ("class keyword",    re.compile(r'\bclass\s+\w+\s*[\{:]'),      2.0),
        ("template",         re.compile(r'\btemplate\s*<'),             3.0),
        ("vector/map/set",   re.compile(r'\bstd::\w+|\bvector<|\bmap<|\bset<'), 2.5),
        ("auto keyword",     re.compile(r'\bauto\s+\w+\s*='),           1.5),
        ("nullptr",          re.compile(r'\bnullptr\b'),                2.5),
        (":: operator",      re.compile(r'\w+::\w+'),                   1.5),
        ("reference",        re.compile(r'\w+\s*&\s*\w+'),              1.5),
    ],
    "Go": [
        ("package keyword",  re.compile(r'\bpackage\s+\w+'),            3.0),
        ("func keyword",     re.compile(r'\bfunc\s+\w+'),               2.5),
        ("import block",     re.compile(r'\bimport\s*\('),              2.5),
        ("goroutine",        re.compile(r'\bgo\s+\w+\(|\bgo\s+func'),   3.0),
        (":= operator",      re.compile(r'\w+\s*:=\s*'),                2.5),
        ("fmt.Print",        re.compile(r'\bfmt\.\w+'),                 2.5),
        ("defer keyword",    re.compile(r'\bdefer\b'),                  2.5),
        ("chan keyword",     re.compile(r'\bchan\b|\bmake\s*\(chan'),    3.0),
        ("error type",       re.compile(r'\berror\b'),                  1.0),
        ("var keyword",      re.compile(r'\bvar\s+\w+'),                1.0),
    ],
    "Rust": [
        ("fn keyword",       re.compile(r'\bfn\s+\w+'),                 2.5),
        ("let mut",          re.compile(r'\blet\s+mut\b|\blet\s+\w+\s*='), 2.0),
        ("use keyword",      re.compile(r'\buse\s+\w+::\w+'),           2.5),
        ("ownership",        re.compile(r'\bborrow\b|\blifetime\b|\b\'[a-z]\b'), 2.0),
        ("println! macro",   re.compile(r'\bprintln!\s*\(|\bprint!\s*\('), 3.0),
        ("impl keyword",     re.compile(r'\bimpl\s+\w+'),               2.5),
        ("enum/struct",      re.compile(r'\b(enum|struct)\s+\w+'),      2.0),
        ("match keyword",    re.compile(r'\bmatch\s+\w+\s*\{'),         2.5),
        ("trait keyword",    re.compile(r'\btrait\s+\w+'),              2.5),
        ("Option/Result",    re.compile(r'\bOption<|\bResult<|\bSome\(|\bNone\b'), 2.5),
    ],
    "PHP": [
        ("<?php tag",        re.compile(r'<\?php'),                     4.0),
        ("$ variable",       re.compile(r'\$\w+'),                      2.0),
        ("echo keyword",     re.compile(r'\becho\s+'),                  2.0),
        ("array function",   re.compile(r'\barray\s*\('),               1.5),
        ("-> operator",      re.compile(r'\$\w+\s*->\s*\w+'),           2.0),
        (":: operator",      re.compile(r'\w+::\w+'),                   1.0),
        ("namespace",        re.compile(r'\bnamespace\s+\w+'),          1.5),
        ("use keyword",      re.compile(r'\buse\s+\w+\\'),              2.0),
        ("function keyword", re.compile(r'\bfunction\s+\w+'),           1.0),
    ],
    "Ruby": [
        ("def/end keywords", re.compile(r'\bdef\s+\w+|\bend\b'),        2.0),
        ("puts/print",       re.compile(r'\bputs\b|\bp\s+\w|\bprint\b'), 2.0),
        ("symbol literal",   re.compile(r':\w+'),                       1.5),
        ("do/end block",     re.compile(r'\bdo\s*\||\bdo\b.*?\bend\b'), 2.0),
        ("require keyword",  re.compile(r'\brequire\s+["\']'),          2.0),
        ("attr_accessor",    re.compile(r'\battr_(accessor|reader|writer)\b'), 3.0),
        ("nil keyword",      re.compile(r'\bnil\b'),                    2.0),
        ("unless keyword",   re.compile(r'\bunless\b'),                 3.0),
        ("interpolation",    re.compile(r'".*?#\{'),                    2.5),
        ("module keyword",   re.compile(r'\bmodule\s+\w+'),             2.0),
    ],
    "Swift": [
        ("var/let",          re.compile(r'\b(var|let)\s+\w+\s*:'),      2.0),
        ("func keyword",     re.compile(r'\bfunc\s+\w+'),               2.0),
        ("import Swift",     re.compile(r'\bimport\s+(Swift|Foundation|UIKit)'), 3.0),
        ("optional type",    re.compile(r'\w+\?\s*[={]|\w+!\s*[={]'),  2.5),
        ("guard let",        re.compile(r'\bguard\s+let\b'),            3.0),
        ("print function",   re.compile(r'\bprint\s*\('),               0.5),
        ("struct/class",     re.compile(r'\b(struct|class|enum)\s+\w+'), 1.5),
        ("protocol keyword", re.compile(r'\bprotocol\s+\w+'),           3.0),
        ("extension keyword",re.compile(r'\bextension\s+\w+'),          2.5),
        ("closure syntax",   re.compile(r'\{\s*\$[0-9]+'),              2.5),
    ],
    "Kotlin": [
        ("fun keyword",      re.compile(r'\bfun\s+\w+'),                2.5),
        ("val/var",          re.compile(r'\b(val|var)\s+\w+'),          2.0),
        ("import kotlin",    re.compile(r'\bimport\s+kotlin\.'),        3.0),
        ("null safety",      re.compile(r'\w+\?\.\w+|\?\?'),            2.5),
        ("data class",       re.compile(r'\bdata\s+class\b'),           3.0),
        ("companion object", re.compile(r'\bcompanion\s+object\b'),     3.0),
        ("when keyword",     re.compile(r'\bwhen\s*\('),                2.5),
        ("println",          re.compile(r'\bprintln\s*\('),             2.0),
        ("extension func",   re.compile(r'\bfun\s+\w+\.\w+'),          2.0),
        ("object keyword",   re.compile(r'\bobject\s+\w+'),             2.0),
    ],
    "SQL": [
        ("SELECT",           re.compile(r'\bSELECT\b', re.I),           2.5),
        ("FROM",             re.compile(r'\bFROM\b', re.I),              1.5),
        ("WHERE",            re.compile(r'\bWHERE\b', re.I),             1.5),
        ("INSERT INTO",      re.compile(r'\bINSERT\s+INTO\b', re.I),    3.0),
        ("UPDATE SET",       re.compile(r'\bUPDATE\b.*\bSET\b', re.I),  3.0),
        ("CREATE TABLE",     re.compile(r'\bCREATE\s+TABLE\b', re.I),   3.0),
        ("JOIN",             re.compile(r'\b(INNER|LEFT|RIGHT|OUTER)?\s*JOIN\b', re.I), 2.0),
        ("GROUP BY",         re.compile(r'\bGROUP\s+BY\b', re.I),       2.5),
        ("ORDER BY",         re.compile(r'\bORDER\s+BY\b', re.I),       2.5),
        ("HAVING",           re.compile(r'\bHAVING\b', re.I),            2.0),
    ],
    "HTML": [
        ("DOCTYPE",          re.compile(r'<!DOCTYPE\s+html>', re.I),    4.0),
        ("html tag",         re.compile(r'<html[\s>]', re.I),           3.0),
        ("head/body tags",   re.compile(r'<(head|body)[\s>]', re.I),    2.5),
        ("div/span tags",    re.compile(r'<(div|span)[\s>]', re.I),     2.0),
        ("href attribute",   re.compile(r'\bhref\s*='),                 2.0),
        ("class attribute",  re.compile(r'\bclass\s*='),                1.5),
        ("closing tag",      re.compile(r'</\w+>'),                     1.0),
        ("self-close tag",   re.compile(r'<(br|hr|img|input)[^>]*/?>'), 2.0),
        ("script tag",       re.compile(r'<script[\s>]', re.I),         2.5),
        ("style tag",        re.compile(r'<style[\s>]', re.I),           2.5),
    ],
    "CSS": [
        ("selector block",   re.compile(r'[\w.#\[\]]+\s*\{[^}]+\}'),   2.0),
        ("property colon",   re.compile(r'\b\w[\w-]*\s*:\s*[^;{]+;'),  1.5),
        ("media query",      re.compile(r'@media\s+'),                  3.0),
        ("color value",      re.compile(r'#[0-9a-fA-F]{3,6}\b|rgba?\('), 1.5),
        ("px/em/rem unit",   re.compile(r'\d+(px|em|rem|vh|vw|%)\b'),   1.5),
        ("important rule",   re.compile(r'!important'),                 2.5),
        ("keyframes",        re.compile(r'@keyframes\s+'),              3.0),
        ("CSS variable",     re.compile(r'--[\w-]+\s*:'),               3.0),
        ("flex/grid",        re.compile(r'\b(flex|grid)\b'),             1.5),
    ],
    "Shell": [
        ("shebang",          re.compile(r'^#!\s*/\w+', re.MULTILINE),   3.0),
        ("echo command",     re.compile(r'\becho\s+'),                  1.5),
        ("$ variable",       re.compile(r'\$\{?\w+\}?'),                1.5),
        ("if/fi",            re.compile(r'\bif\b.*;\s*then|\bfi\b'),    2.5),
        ("for/do/done",      re.compile(r'\bfor\b.*\bdo\b|\bdone\b'),   2.5),
        ("pipe operator",    re.compile(r'\|\s*\w+'),                   1.0),
        ("grep/sed/awk",     re.compile(r'\b(grep|sed|awk|cut|sort)\b'), 2.0),
        ("export keyword",   re.compile(r'\bexport\s+\w+='),            2.5),
        ("function def",     re.compile(r'\w+\s*\(\s*\)\s*\{'),         2.0),
        ("here-doc",         re.compile(r'<<\s*\w+'),                   2.5),
    ],
    "R": [
        ("assignment",       re.compile(r'\w+\s*<-\s*'),                3.0),
        ("library/require",  re.compile(r'\b(library|require)\s*\('),   3.0),
        ("c() function",     re.compile(r'\bc\s*\('),                   2.0),
        ("data.frame",       re.compile(r'\bdata\.frame\s*\('),         3.0),
        ("NA/NULL",          re.compile(r'\bNA\b|\bNULL\b|\bTRUE\b|\bFALSE\b'), 2.0),
        ("ggplot",           re.compile(r'\bggplot\s*\('),              3.0),
        ("function keyword", re.compile(r'\bfunction\s*\('),            1.5),
        ("vector index",     re.compile(r'\w+\[\d+\]|\w+\[,\d+\]'),    1.5),
        ("print/cat",        re.compile(r'\bprint\s*\(|\bcat\s*\('),    1.0),
    ],
}


class ProgrammingLanguageDetector:
    """Detect the programming language of a code snippet."""

    def detect(self, code: str) -> ProgrammingDetectionResult:
        """Detect the programming language of the given code snippet.

        Args:
            code: Source code text.

        Returns:
            ProgrammingDetectionResult with language, confidence, and matched features.

        Raises:
            ValueError: If code is empty.
        """
        if not code or not code.strip():
            raise ValueError("Input code must not be empty")

        scores, matched = self._score_all(code)

        if not scores:
            return ProgrammingDetectionResult(language="Unknown", confidence=0.0)

        best = max(scores, key=scores.__getitem__)
        total = sum(scores.values()) or 1
        confidence = round(scores[best] / total, 4)

        return ProgrammingDetectionResult(
            language=best,
            confidence=confidence,
            matched_features=matched.get(best, []),
        )

    def detect_all(self, code: str, top_n: int = 3) -> list[ProgrammingDetectionResult]:
        """Return top N programming language candidates sorted by confidence.

        Args:
            code: Source code text.
            top_n: Maximum number of results to return.

        Returns:
            List of ProgrammingDetectionResult sorted by descending confidence.
        """
        if not code or not code.strip():
            raise ValueError("Input code must not be empty")

        scores, matched = self._score_all(code)
        total = sum(scores.values()) or 1

        results = [
            ProgrammingDetectionResult(
                language=lang,
                confidence=round(scores[lang] / total, 4),
                matched_features=matched.get(lang, []),
            )
            for lang in scores
        ]
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results[:top_n]

    def _score_all(
        self, code: str
    ) -> tuple[dict[str, float], dict[str, list[str]]]:
        scores: dict[str, float] = {}
        matched: dict[str, list[str]] = {}

        for language, rules in _RULES.items():
            lang_score = 0.0
            lang_features: list[str] = []
            for feature_name, pattern, weight in rules:
                if pattern.search(code):
                    lang_score += weight
                    lang_features.append(feature_name)
            if lang_score > 0:
                scores[language] = lang_score
                matched[language] = lang_features

        return scores, matched
