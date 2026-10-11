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
    """Punto decimal y grupos finos desde cinco cifras, sin perder ceros."""
    raw = raw.replace(r"\,", "").replace("{,}", ".").strip()
    scientific = re.fullmatch(r"(.+?)[eE]([+-]?\d+)", raw)
    if scientific:
        return format_number(scientific[1]) + rf"\cdot10^{{{int(scientific[2])}}}"
    integer, dot, decimal = raw.partition(".")
    sign = ""
    if integer.startswith(("-", "+")):
        sign, integer = integer[0], integer[1:]
    integer = integer or "0"
    if len(integer) >= 5:
        integer = re.sub(r"(?<=\d)(?=(?:\d{3})+$)", lambda _: r"\,", integer)
    return sign + integer + ("." + decimal if dot else "")


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


# Solo tokens numéricos completos: nunca interpretar comas de listas como decimales.
NUMBER = re.compile(
    r"(?<![\w.])(?:\d+(?:\\,\d{3})*(?:(?:\.|\{,\})\d+(?:\\,\d{3})*)?|\.\d+)"
    r"(?:[eE][+-]?\d+)?(?!\d|\.\d)"
)
UNIT_FACTOR = re.compile(r"([A-Za-z]+)(?:\^(?:\{(-?\d+)\}|(-?\d+)))?")


def normalize_unit(raw: str) -> str:
    """Cocientes de símbolos en redonda -> producto con potencias negativas."""
    parts = raw.split("/")
    if len(parts) != 2:
        return raw
    result = []
    for index, part in enumerate(parts):
        factors = list(UNIT_FACTOR.finditer(part))
        rest = UNIT_FACTOR.sub("", part).replace(r"\,", "").strip()
        if not factors or rest:
            return raw
        for factor in factors:
            power = int(factor[2] or factor[3] or 1) * (-1 if index else 1)
            result.append(factor[1] + (rf"^{{{power}}}" if power != 1 else ""))
    return r"\,".join(result)


def normalize_math(body: str) -> str:
    body = normalize_distributions(expand_custom_macros(body))
    body = body.replace("−", "-").replace("{,}", ".")
    body = re.sub(r"(\\[A-Za-z]+)([0-9]+(?:\\,[0-9]{3})*(?:\.[0-9]+(?:\\,[0-9]{3})*)?)",
                  lambda m: m[1] + format_number(m[2]), body)
    body = NUMBER.sub(lambda m: format_number(m[0]), body)
    body = re.sub(r"\\(?:times|dot)(?=\s*10\s*\^)", r"\\cdot", body)
    body = re.sub(
        r"\\mathrm\{((?:[^{}]|\{[^{}]*\})*)\}",
        lambda m: rf"\mathrm{{{normalize_unit(m[1])}}}", body,
    )
    # El espacio fino es común a HTML/MathJax y PDF/LaTeX.
    body = re.sub(r"(?<=[\d}])\s*(?=\\mathrm\{)", lambda _: r"\,", body)
    body = re.sub(r"(?P<expr>\d|[A-Za-z]|\})(?:\s|\\,|\\;|\\ |~)*\\%",
                  lambda m: m['expr'] + r"\,\%", body)
    return body


def normalize_qmd(text: str) -> str:
    # Conservar metadatos, URLs y bloques de código; transformar únicamente fórmulas.
    def prose(text: str) -> str:
        text = text.replace(r"\(", "$").replace(r"\)", "$")
        text = text.replace(r"\[", "$$").replace(r"\]", "$$")
        return re.sub(
            r"(?<!\\)(?P<delimiter>\$\$|\$)(?P<body>.*?)(?<!\\)(?P=delimiter)",
            lambda m: m['delimiter'] + normalize_math(m['body']) + m['delimiter'],
            text, flags=re.DOTALL,
        )

    protected = re.compile(r"\A---\n.*?\n---(?:\n|$)|^([`~]{3,})[^\n]*\n.*?^\1[^\n]*(?:\n|$)|`[^`\n]+`",
                           re.MULTILINE | re.DOTALL)
    result, cursor = [], 0
    for match in protected.finditer(text):
        result.extend((prose(text[cursor:match.start()]), match[0]))
        cursor = match.end()
    result.append(prose(text[cursor:]))
    return "".join(result)


def normalize_tex(text: str) -> str:
    # Los fragmentos PAES existentes contienen también cantidades sin delimitadores.
    text = re.sub(r"\\SI\{(-?\d+(?:\.\d+)?)\}\[\\\$\]\{\}",
                  lambda m: rf"\${format_number(m[1])}", text)
    text = re.sub(r"\\(?:SI|qty)\{([^{}]+)\}\{([^{}]+)\}",
                  lambda m: rf"{format_number(m[1])}\,\mathrm{{{m[2]}}}", text)
    text = re.sub(r"\\(?:si|unit)\{([^{}]+)\}", lambda m: rf"\mathrm{{{m[1]}}}", text)
    text = re.sub(r"\\num\{([^{}]+)\}", lambda m: format_number(m[1]), text)
    return normalize_math(text)


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
        if path.is_relative_to(ROOT / "includes"):
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
        r"\\(?:SI|si|num|qty|unit)\{": "use LaTeX estándar explícito",
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
        if path.is_relative_to(ROOT / "includes"):
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
    print("Notación matemática válida: punto decimal, agrupación desde cinco cifras y unidades en redonda.")
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
