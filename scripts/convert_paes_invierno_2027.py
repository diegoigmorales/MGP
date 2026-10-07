#!/usr/bin/env python3
"""Convierte los fragmentos LaTeX de PAES M1 Invierno 2027 a páginas Quarto."""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

from build_registry import KNOWLEDGE_TAG_RE, discover, next_tag


ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "contenidos" / "paes" / "m1" / "admision-2027-invierno"

COMMAND_RE = re.compile(
    r"\\SI\{(?P<si_value>[^{}]*)\}(?:\[(?P<si_prefix>[^]]*)\])?\{(?P<si_unit>[^{}]*)\}"
    r"|\\num\{(?P<num>[^{}]*)\}"
    r"|\\si\{(?P<unit>[^{}]*)\}"
    r"|\\ang\{(?P<angle>[^{}]*)\}"
)


def math_state_at(line: str, position: int, initial: bool) -> bool:
    state = initial
    i = 0
    while i < position:
        if line.startswith(r"\[", i) or line.startswith(r"\(", i):
            state = True
            i += 2
        elif line.startswith(r"\]", i) or line.startswith(r"\)", i):
            state = False
            i += 2
        elif line[i] == "$" and (i == 0 or line[i - 1] != "\\"):
            width = 2 if line.startswith("$$", i) else 1
            state = not state
            i += width
        else:
            i += 1
    return state


def final_math_state(line: str, initial: bool) -> bool:
    return math_state_at(line, len(line), initial)


def format_unit(unit: str) -> str:
    if not unit:
        return ""
    if unit == r"\%":
        return unit
    if r"\pi" in unit:
        return unit
    return rf"\mathrm{{{unit}}}"


def replace_commands(line: str, initial_math_state: bool) -> str:
    def replacement(match: re.Match[str]) -> str:
        if match.group("num") is not None:
            expression = match.group("num")
        elif match.group("angle") is not None:
            expression = rf"{match.group('angle')}^\circ"
        elif match.group("unit") is not None:
            expression = format_unit(match.group("unit"))
        else:
            value = match.group("si_value")
            prefix = match.group("si_prefix") or ""
            unit = match.group("si_unit")
            if prefix == r"\$" and not unit:
                expression = rf"\${value}"
            else:
                formatted_unit = format_unit(unit)
                separator = r"\," if formatted_unit else ""
                expression = f"{prefix}{value}{separator}{formatted_unit}"

        if math_state_at(line, match.start(), initial_math_state):
            return expression
        return f"${expression}$"

    return COMMAND_RE.sub(replacement, line)


def convert_question(source: str, number: int, tag: str) -> str:
    body = re.sub(r"^\s*\\begin\{problem\}\s*", "", source)
    body = re.sub(r"\s*\\end\{problem\}\s*$", "", body)
    body = textwrap.dedent(body).strip()

    converted: list[str] = []
    list_kind: str | None = None
    choice = 0
    in_display_math = False

    for original_line in body.splitlines():
        stripped = original_line.strip()
        if stripped.startswith(r"\begin{enumerate}"):
            list_kind = "enumerate"
            choice = 0
            converted.extend(["", "::: {.answer-options}"])
            continue
        if stripped == r"\end{enumerate}":
            list_kind = None
            converted.extend([":::", ""])
            continue
        if stripped == r"\begin{itemize}":
            list_kind = "itemize"
            converted.append("")
            continue
        if stripped == r"\end{itemize}":
            list_kind = None
            converted.append("")
            continue
        if stripped == r"\begin{center}":
            converted.extend(["", "::: {.text-center}"])
            continue
        if stripped == r"\end{center}":
            converted.extend([":::", ""])
            continue

        line = original_line.strip() if original_line.startswith("    ") else original_line
        item = re.match(r"\s*\\item\s+(.*)", line)
        if item:
            marker = "-"
            if list_kind == "enumerate":
                marker = "1."
                choice += 1
            line = f"{marker} {item.group(1)}"

        if stripped == r"\[":
            line = "$$"
        elif stripped == r"\]":
            line = "$$"

        converted.append(replace_commands(line, in_display_math).rstrip())
        in_display_math = final_math_state(original_line, in_display_math)

    title = f"Pregunta {number} · PAES M1 Invierno — Admisión 2027"
    header = [
        "---",
        f'title: "{title}"',
        f"paes-question: {number}",
        f'knowledge-tag: "{tag}"',
        "---",
        "",
        "",
    ]
    return "\n".join(header + converted + [""])


def build_index() -> str:
    lines = [
        "---",
        'title: "PAES M1 Invierno — Admisión 2027"',
        'description: "Preguntas de la PAES de Competencia Matemática M1 de Invierno para el proceso de Admisión 2027."',
        "---",
        "",
        "# Preguntas",
        "",
        "Las preguntas se presentan como páginas individuales para facilitar su consulta, enlace y análisis posterior.",
        "",
    ]
    for number in range(1, 66):
        lines.append(f"- [Pregunta {number}](pregunta-{number:02d}.qmd)")
    return "\n".join(lines) + "\n"


def main() -> int:
    sources = sorted(QUESTIONS.glob("pregunta-*.tex"))
    if len(sources) != 65:
        raise SystemExit(f"Se esperaban 65 archivos TeX y se encontraron {len(sources)}")

    objects, errors = discover()
    if errors:
        raise SystemExit("\n".join(errors))
    used = {obj["tag"] for obj in objects}
    for number, source in enumerate(sources, 1):
        destination = source.with_suffix(".qmd")
        previous = KNOWLEDGE_TAG_RE.search(destination.read_text(encoding="utf-8")) if destination.exists() else None
        tag = previous.group(1) if previous else next_tag(used)
        used.add(tag)
        destination.write_text(convert_question(source.read_text(encoding="utf-8"), number, tag), encoding="utf-8")

    (QUESTIONS / "index.qmd").write_text(build_index(), encoding="utf-8")
    print("Conversión terminada: 65 preguntas QMD y un índice.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
