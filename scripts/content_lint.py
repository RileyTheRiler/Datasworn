#!/usr/bin/env python3
"""Content quality linter for narrative assets.

This tool scans data files for common quality issues:
- Readability: highlights dense sentences with poor readability.
- Banned phrases: blocks lorem ipsum and other placeholder text.
- Placeholder coverage: surfaces unresolved template markers.
- Inconsistent voice: flags first-person mixed with second-person instructions.

Usage:
    python scripts/content_lint.py [paths...]

If no paths are provided the linter inspects ``data/`` and ``src/prompts``.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass
from typing import Iterable, List, Sequence

# Thresholds chosen to avoid false positives while surfacing obvious problems.
READABILITY_FLOOR = 30.0

BANNED_PHRASES = {
    "lorem ipsum",
    "to be decided",
    "tbd",
    "coming soon",
    "dummy text",
}

PLACEHOLDER_PATTERN = re.compile(r"(?:TODO|TBD|PLACEHOLDER|<placeholder>|\[placeholder\])", re.IGNORECASE)

FIRST_PERSON = re.compile(r"\b(i|me|my|mine|i'm)\b", re.IGNORECASE)
SECOND_PERSON = re.compile(r"\b(you|your|yours|you're|you'll)\b", re.IGNORECASE)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".json", ".yaml", ".yml"}


@dataclass
class Issue:
    path: pathlib.Path
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def readability_score(text: str) -> float:
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return 100.0

    words = [w for s in sentences for w in re.findall(r"[A-Za-z']+", s)]
    if not words:
        return 100.0

    syllables = sum(max(1, len(re.findall(r"[aeiouyAEIOUY]+", w))) for w in words)
    avg_words_per_sentence = len(words) / len(sentences)
    avg_syllables_per_word = syllables / len(words)

    return 206.835 - 1.015 * avg_words_per_sentence - 84.6 * avg_syllables_per_word


def iter_files(paths: Sequence[pathlib.Path]) -> Iterable[pathlib.Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield path
            continue
        for candidate in path.rglob("*"):
            if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield candidate


def is_narrative_line(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 30 or " " not in stripped:
        return False
    alpha_ratio = sum(ch.isalpha() for ch in stripped) / len(stripped)
    if alpha_ratio < 0.65:
        return False
    if stripped[0] in "{[" and stripped.endswith(("}", "]")):
        return False
    return True


def lint_line(path: pathlib.Path, line_no: int, line: str, *, enable_readability: bool) -> List[Issue]:
    issues: List[Issue] = []
    lowered = line.lower()

    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            issues.append(Issue(path, line_no, f"Banned phrase detected: '{phrase}'"))

    if PLACEHOLDER_PATTERN.search(line):
        issues.append(Issue(path, line_no, "Unresolved placeholder text"))

    if FIRST_PERSON.search(line) and SECOND_PERSON.search(line):
        issues.append(Issue(path, line_no, "Mixed first- and second-person voice"))

    if enable_readability and is_narrative_line(line):
        score = readability_score(line)
        if score < READABILITY_FLOOR:
            issues.append(Issue(path, line_no, f"Low readability score ({score:.1f})"))

    return issues


def lint_paths(paths: Sequence[pathlib.Path]) -> List[Issue]:
    problems: List[Issue] = []
    for file_path in iter_files(paths):
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        enable_readability = file_path.suffix.lower() in {".txt", ".md"}
        for idx, line in enumerate(content.splitlines(), start=1):
            problems.extend(lint_line(file_path, idx, line, enable_readability=enable_readability))
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint narrative content for quality issues")
    parser.add_argument(
        "paths",
        nargs="*",
        type=pathlib.Path,
        help="Paths to scan (defaults to data/ and src/prompts)",
    )
    args = parser.parse_args(argv)

    target_paths = args.paths or [pathlib.Path("data"), pathlib.Path("src/prompts")]
    issues = lint_paths(target_paths)

    if issues:
        for issue in issues:
            print(issue.format())
        return 1

    print("content_lint: no issues found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
