#!/usr/bin/env python3
"""Normaliza y valida la notación matemática compartida por QMD y TeX."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", ".quarto", "_book", "_freeze", "_generated", "_site"}
DISTRIBUTION_NAMES = (
    "Bernoulli", "Binomial", "Exponencial", "Geométrica", "Hipergeométrica",
    "Multinomial", "Poisson", "Uniforme",
)
DISTRIBUTION_NAME_PATTERN = "|".join(
    sorted(map(re.escape, DISTRIBUTION_NAMES), key=len, reverse=True)
)
DISTRIBUTION_PATTERN = DISTRIBUTION_NAME_PATTERN + "|N"


def sources(suffix: str) -> list[Path]:
    return [
        path
        for path in ROOT.rglob(f"*{suffix}")
        if not any(part in IGNORED for part in path.relative_to(ROOT).parts)
    ]


def format_number(raw: str) -> str:
    raw = raw.replace(r"\,", "").strip()
    if "." in raw:
        integer, decimal = raw.split(".", 1)
    else:
        integer, decimal = raw, ""
    sign = ""
    if integer.startswith("-"):
        sign, integer = "-", integer[1:]
    groups: list[str] = []
    while len(integer) > 3:
        groups.insert(0, integer[-3:])
        integer = integer[:-3]
    groups.insert(0, integer or "0")
    result = sign + r"\,".join(groups)
    if decimal:
        result += "{,}" + decimal
    return result


def expand_custom_macros(text: str) -> str:
    """Retira las macros locales antiguas y deja TeX estándar explícito."""
    arities = {"numero": 1, "unidad": 1, "cantidad": 2, "porcentaje": 1, "pesos": 1}

    def read_group(source: str, start: int) -> tuple[str, int] | None:
        if start >= len(source) or source[start] != "{":
            return None
        depth = 0
        for index in range(start, len(source)):
            if source[index] == "{":
                depth += 1
            elif source[index] == "}":
                depth -= 1
                if depth == 0:
                    return source[start + 1:index], index + 1
        return None

    while True:
        match = re.search(r"\\(numero|unidad|cantidad|porcentaje|pesos)\{", text)
        if not match:
            return text
        name = match.group(1)
        cursor = match.end() - 1
        arguments: list[str] = []
        for _ in range(arities[name]):
            group = read_group(text, cursor)
            if group is None:
                return text
            argument, cursor = group
            arguments.append(argument)
        if name == "numero":
            replacement = arguments[0]
        elif name == "unidad":
            replacement = rf"\mathrm{{{arguments[0]}}}"
        elif name == "cantidad":
            replacement = rf"{arguments[0]}\,\mathrm{{{arguments[1]}}}"
        elif name == "porcentaje":
            replacement = rf"{arguments[0]}\,\%"
        else:
            replacement = rf"\${arguments[0]}"
        text = text[:match.start()] + replacement + text[cursor:]


def normalize_distributions(body: str) -> str:
    """Escribe distribuciones con operatorname sin introducir macros propias."""
    body = re.sub(r"\\mathcal\s*\{?N\}?", r"\\operatorname{N}", body)
    body = re.sub(r"\\mathrm\{Normal\}", r"\\operatorname{N}", body)
    body = re.sub(
        rf"\\mathrm\{{(?P<name>{DISTRIBUTION_NAME_PATTERN})\}}",
        lambda match: rf"\operatorname{{{match.group('name')}}}",
        body,
    )
    body = re.sub(
        r"\\mathrm\{N\}(?=\s*(?:\\left)?\()",
        r"\\operatorname{N}",
        body,
    )
    body = re.sub(
        r"\\operatorname\{Normal\}",
        r"\\operatorname{N}",
        body,
    )
    body = re.sub(
        rf"(?P<prefix>\\sim\s*)(?P<name>{DISTRIBUTION_PATTERN}|Normal)(?=\s*(?:\\left)?\()",
        lambda match: match.group("prefix") + rf"\operatorname{{{'N' if match.group('name') == 'Normal' else match.group('name')}}}",
        body,
    )
    return body


def normalize_qmd(text: str) -> str:
    text = expand_custom_macros(text)
    text = text.replace(r"\(", "$").replace(r"\)", "$")
    text = re.sub(
        r"\\\$(?P<num>\d+(?:\\,\d{3})*(?:\.\d+)?)",
        lambda m: rf"\${format_number(m.group('num'))}",
        text,
    )
    text = re.sub(
        r"(?P<num>\d+(?:\.\d+)?)(?:\\,)?\\%",
        lambda m: rf"{format_number(m.group('num'))}\,\%",
        text,
    )

    def math_body(match: re.Match[str]) -> str:
        delimiter = match.group("delimiter")
        body = normalize_distributions(match.group("body"))
        body = re.sub(
            r"(?P<num>\d+(?:\.\d+|\{,\}\d+)?)\\,\\pi m\^3",
            lambda item: rf"{format_number(item.group('num').replace('{,}', '.'))}\pi\,\mathrm{{m^3}}",
            body,
        )
        stripped = body.strip()
        percentage = re.fullmatch(r"(?P<expr>.+?)(?:\\,)?\\%", stripped, re.DOTALL)
        if percentage:
            body = body.replace(stripped, rf"{percentage.group('expr')}\,\%")
        body = re.sub(r"(?<![A-Za-z0-9])(?P<int>\d+)\.(?P<dec>\d+)(?!\d)", r"\g<int>{,}\g<dec>", body)
        body = re.sub(
            r"(?<![A-Za-z0-9])(?<!\{,\})(?P<num>\d{4,})(?![A-Za-z0-9])",
            lambda item: format_number(item.group("num")),
            body,
        )
        return delimiter + body + delimiter

    text = re.sub(
        r"(?<!\\)(?P<delimiter>\$\$|\$)(?P<body>.*?)(?<!\\)(?P=delimiter)",
        math_body,
        text,
        flags=re.DOTALL,
    )
    return text


def normalize_tex(text: str) -> str:
    text = expand_custom_macros(text)
    text = normalize_distributions(text)
    text = re.sub(
        r"\\SI\{(?P<num>-?\d+(?:\.\d+)?)\}\[\\\$\]\{\}",
        lambda m: rf"\${format_number(m.group('num'))}",
        text,
    )

    def quantity(match: re.Match[str]) -> str:
        number = format_number(match.group("num"))
        unit = match.group("unit")
        if unit.startswith(r"\pi "):
            return rf"{number}\pi\,\mathrm{{{unit[4:]}}}"
        return rf"{number}\,\mathrm{{{unit}}}"

    text = re.sub(
        r"\\SI\{(?P<num>-?\d+(?:\.\d+)?)\}\{(?P<unit>[^{}]+)\}",
        quantity,
        text,
    )
    text = re.sub(
        r"\\si\{(?P<unit>[^{}]+)\}",
        lambda m: rf"\mathrm{{{m.group('unit')}}}",
        text,
    )
    text = re.sub(
        r"\\num\{(?P<num>-?\d+(?:\.\d+)?)\}",
        lambda m: format_number(m.group("num")),
        text,
    )
    text = re.sub(
        r"(?P<num>\d+(?:\.\d+)?)(?:\\,)?\\%",
        lambda m: rf"{format_number(m.group('num'))}\,\%",
        text,
    )

    def inline_math(match: re.Match[str]) -> str:
        body = match.group("body")
        stripped = body.strip()
        percentage = re.fullmatch(r"(?P<expr>.+?)(?:\\,)?\\%", stripped, re.DOTALL)
        if percentage:
            body = body.replace(stripped, rf"{percentage.group('expr')}\,\%")
        return "$" + body + "$"

    text = re.sub(r"(?<!\\)\$(?P<body>.*?)(?<!\\)\$", inline_math, text, flags=re.DOTALL)
    return text


def normalize(write: bool) -> int:
    changed: list[Path] = []
    for path in sources(".qmd"):
        old = path.read_text(encoding="utf-8-sig")
        new = normalize_qmd(old)
        if new != old:
            changed.append(path)
            if write:
                path.write_text(new, encoding="utf-8", newline="\n")
    for path in sources(".tex"):
        if path == ROOT / "includes" / "math-macros.tex":
            continue
        old = path.read_text(encoding="utf-8-sig")
        new = normalize_tex(old)
        if new != old:
            changed.append(path)
            if write:
                path.write_text(new, encoding="utf-8", newline="\n")
    action = "normalizados" if write else "por normalizar"
    print(f"Archivos {action}: {len(changed)}")
    for path in changed:
        print(path.relative_to(ROOT).as_posix())
    return 0


def check() -> int:
    errors: list[str] = []
    qmd_rules = {
        r"\\\(|\\\)": "use $...$ para matemática en línea",
        r"\\\[|\\\]": "use $$...$$ para matemática desplegada",
        r"\\(?:numero|unidad|cantidad|porcentaje|pesos)\{": "no use macros locales no solicitadas",
        rf"\\mathcal\s*\{{?N\}}?|\\mathrm\{{(?:{DISTRIBUTION_NAME_PATTERN}|Normal)\}}|\\mathrm\{{N\}}(?=\s*(?:\\left)?\()": "use \\operatorname para distribuciones",
    }
    tex_rules = {
        r"\\(?:SI|si|num)\{": "use LaTeX estándar explícito",
        r"\\usepackage(?:\[[^]]*\])?\{siunitx\}": "siunitx no está permitido",
        r"\\(?:numero|unidad|cantidad|porcentaje|pesos)\{": "no use macros locales no solicitadas",
        rf"\\mathcal\s*\{{?N\}}?|\\mathrm\{{(?:{DISTRIBUTION_NAME_PATTERN}|Normal)\}}|\\mathrm\{{N\}}(?=\s*(?:\\left)?\()": "use \\operatorname para distribuciones",
    }
    for path in sources(".qmd"):
        text = path.read_text(encoding="utf-8-sig")
        for pattern, message in qmd_rules.items():
            for match in re.finditer(pattern, text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(ROOT)}:{line}: {message}")
        if normalize_qmd(text) != text:
            errors.append(f"{path.relative_to(ROOT)}: quedan números o magnitudes por normalizar")
    for path in sources(".tex"):
        if path == ROOT / "includes" / "math-macros.tex":
            continue
        text = path.read_text(encoding="utf-8-sig")
        for pattern, message in tex_rules.items():
            for match in re.finditer(pattern, text):
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{path.relative_to(ROOT)}:{line}: {message}")
        if normalize_tex(text) != text:
            errors.append(f"{path.relative_to(ROOT)}: queda notación matemática por normalizar")
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors), file=sys.stderr)
        return 1
    print("Notación matemática válida: LaTeX estándar y sin macros locales.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="reescribe las fuentes")
    parser.add_argument("--check", action="store_true", help="valida las convenciones")
    args = parser.parse_args()
    if args.check:
        return check()
    return normalize(args.write)


if __name__ == "__main__":
    raise SystemExit(main())
