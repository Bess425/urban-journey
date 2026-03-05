"""Tests for programming language detection."""

import pytest
from universal_language_detection import ProgrammingLanguageDetector


@pytest.fixture
def detector():
    return ProgrammingLanguageDetector()


PYTHON_CODE = """\
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)

class Calculator:
    def __init__(self):
        self.result = None

    def compute(self, x: int, y: int) -> int:
        return x + y

if __name__ == "__main__":
    calc = Calculator()
    print(calc.compute(3, 4))
"""

JAVASCRIPT_CODE = """\
const greet = (name) => {
    console.log(`Hello, ${name}!`);
};

async function fetchData(url) {
    const response = await fetch(url);
    const data = await response.json();
    return data;
}

let count = 0;
if (count === 0) {
    greet('World');
}
"""

GO_CODE = """\
package main

import (
    "fmt"
    "sync"
)

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    fmt.Printf("Worker %d starting\\n", id)
}

func main() {
    var wg sync.WaitGroup
    for i := 1; i <= 5; i++ {
        wg.Add(1)
        go worker(i, &wg)
    }
    wg.Wait()
}
"""

RUST_CODE = """\
use std::collections::HashMap;

fn main() {
    let mut scores: HashMap<String, u32> = HashMap::new();
    scores.insert(String::from("Alice"), 10);

    if let Some(score) = scores.get("Alice") {
        println!("Alice's score: {}", score);
    }

    let numbers: Vec<i32> = (1..=5).collect();
    let doubled: Vec<i32> = numbers.iter().map(|&x| x * 2).collect();
    println!("{:?}", doubled);
}
"""

SQL_CODE = """\
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.active = 1
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 5
ORDER BY order_count DESC;
"""

HTML_CODE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Hello World</h1>
        <p>This is a paragraph.</p>
    </div>
    <script src="app.js"></script>
</body>
</html>
"""

JAVA_CODE = """\
import java.util.ArrayList;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<String> items = new ArrayList<>();
        items.add("Hello");
        items.add("World");
        for (String item : items) {
            System.out.println(item);
        }
    }
}
"""


class TestDetect:
    def test_python(self, detector):
        result = detector.detect(PYTHON_CODE)
        assert result.language == "Python"
        assert result.confidence > 0.1

    def test_javascript(self, detector):
        result = detector.detect(JAVASCRIPT_CODE)
        assert result.language == "JavaScript"
        assert result.confidence > 0.1

    def test_go(self, detector):
        result = detector.detect(GO_CODE)
        assert result.language == "Go"
        assert result.confidence > 0.1

    def test_rust(self, detector):
        result = detector.detect(RUST_CODE)
        assert result.language == "Rust"
        assert result.confidence > 0.1

    def test_sql(self, detector):
        result = detector.detect(SQL_CODE)
        assert result.language == "SQL"
        assert result.confidence > 0.1

    def test_html(self, detector):
        result = detector.detect(HTML_CODE)
        assert result.language == "HTML"
        assert result.confidence > 0.1

    def test_java(self, detector):
        result = detector.detect(JAVA_CODE)
        assert result.language == "Java"
        assert result.confidence > 0.1

    def test_empty_raises(self, detector):
        with pytest.raises(ValueError):
            detector.detect("")

    def test_matched_features_non_empty(self, detector):
        result = detector.detect(PYTHON_CODE)
        assert len(result.matched_features) > 0

    def test_confidence_between_0_and_1(self, detector):
        result = detector.detect(PYTHON_CODE)
        assert 0.0 <= result.confidence <= 1.0


class TestDetectAll:
    def test_returns_list(self, detector):
        results = detector.detect_all(PYTHON_CODE)
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_sorted_by_confidence(self, detector):
        results = detector.detect_all(PYTHON_CODE)
        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)

    def test_top_n_respected(self, detector):
        results = detector.detect_all(PYTHON_CODE, top_n=2)
        assert len(results) <= 2

    def test_empty_raises(self, detector):
        with pytest.raises(ValueError):
            detector.detect_all("")
