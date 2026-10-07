#!/usr/bin/env python3
"""Valida los objetos de conocimiento y genera el registro derivado."""

from __future__ import annotations

import json
import posixpath
import re
import shlex
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "_generated"
TAG_RE = re.compile(r"^[0-9A-Z]{4}$")
OPEN_RE = re.compile(r"^\s*:{3,}\s*\{([^}]*)\}\s*$")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(?P<yaml>.*?)\n---(?:\s*\n|\Z)", re.DOTALL)
PAES_NUMBER_RE = re.compile(r"^paes-question:\s*(\d+)\s*$", re.MULTILINE)
KNOWLEDGE_TAG_RE = re.compile(r'^knowledge-tag:\s*"([0-9A-Z]{4})"\s*$', re.MULTILINE)
TITLE_RE = re.compile(r'^title:\s*"(.*?)"\s*$', re.MULTILINE)
NATIVE_LABEL_RE = re.compile(r"\{#(?P<label>(?:def|prp|thm|lem|cor|exm|rem|concept)-[0-9A-Z]{4})(?=\s|\})")
ENRICHED_CHAPTERS = {
    "contenidos/libro/algebra/potencias-raices-logaritmos.qmd",
    "contenidos/libro/algebra/algebra-elemental.qmd",
    "contenidos/libro/algebra/ecuaciones-inecuaciones.qmd",
    "contenidos/libro/algebra/sucesiones-series.qmd",
    "contenidos/libro/algebra/funciones.qmd",
    "contenidos/libro/probabilidad/combinatoria-probabilidad.qmd",
    "contenidos/libro/estadistica/index.qmd",
}
ENV_PREFIX = {"principio": "prp", "propiedad": "prp", "teorema": "thm", "definicion": "def"}
DEFINITION_REPRESENTATIONS = {"008W", "007V"}
RELATIONS = {
    "usa",
    "requiere",
    "demuestra",
    "generaliza",
    "especializa",
    "relacionado",
    "error_asociado",
    "alternativa",
    "prerequisito",
    "pertenece_a",
    "evalua",
    "profundiza",
    "aplica",
    "similar_a",
}


def parse_attributes(raw: str) -> tuple[set[str], dict[str, str]]:
    classes: set[str] = set()
    attrs: dict[str, str] = {}
    for token in shlex.split(raw, posix=True):
        if token.startswith("."):
            classes.add(token[1:])
        elif token.startswith("#"):
            attrs["id"] = token[1:]
        elif "=" in token:
            key, value = token.split("=", 1)
            attrs[key.replace("-", "_")] = value
    return classes, attrs



ENVIRONMENT_STYLES = {
    "def": "definition", "prp": "plain", "thm": "plain",
    "lem": "plain", "cor": "plain", "cnj": "plain", "axm": "plain",
    "exm": "remark", "rem": "remark",
}


def validate_environments(source: str, relpath: str) -> list[str]:
    """Impide barras que agrupen un enunciado y su ejemplo."""
    errors: list[str] = []
    stack: list[tuple[str, int]] = []
    code_fence = None
    for lineno, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        code_match = re.match(r"^(`{3,}|~{3,})", stripped)
        if code_match:
            fence = code_match.group(1)[0]
            if code_fence is None:
                code_fence = fence
            elif fence == code_fence:
                code_fence = None
            continue
        if code_fence:
            continue
        match = OPEN_RE.match(line)
        if match:
            classes, attrs = parse_attributes(match.group(1))
            prefix = attrs.get("id", "").split("-", 1)[0]
            style = ENVIRONMENT_STYLES.get(prefix)
            if style:
                if not TAG_RE.fullmatch(attrs.get("data_environment_tag", "")):
                    errors.append(f"{relpath}:{lineno}: el entorno requiere data-environment-tag válido")
                expected = f"theorem-style-{style}"
                if expected not in classes:
                    errors.append(f"{relpath}:{lineno}: falta .{expected}")
                if any(parent in ENVIRONMENT_STYLES for parent, _ in stack):
                    errors.append(f"{relpath}:{lineno}: un entorno formal no debe contener otro entorno")
            if "knowledge-object" in classes and any(c.startswith("theorem-style-") for c in classes):
                errors.append(f"{relpath}:{lineno}: el contenedor de identidad no debe llevar barra")
            stack.append((prefix, lineno))
        elif re.fullmatch(r":{3,}", stripped):
            if not stack:
                errors.append(f"{relpath}:{lineno}: cierre de entorno sin apertura")
            else:
                stack.pop()
    for _, lineno in stack:
        errors.append(f"{relpath}:{lineno}: entorno sin cierre")
    return errors


def discover() -> tuple[list[dict], list[str]]:
    objects: list[dict] = []
    errors: list[str] = []
    native_labels: dict[str, tuple[str, int]] = {}
    environment_tags: dict[str, tuple[str, int]] = {}
    ignored = {"_site", "_book", ".quarto", ".git", "_generated"}
    for path in sorted(ROOT.rglob("*.qmd")):
        if any(part in ignored for part in path.relative_to(ROOT).parts):
            continue
        relpath = path.relative_to(ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        errors.extend(validate_environments(source, relpath))
        for label_match in NATIVE_LABEL_RE.finditer(source):
            label = label_match.group("label")
            line = source.count("\n", 0, label_match.start()) + 1
            if label in native_labels:
                first_source, first_line = native_labels[label]
                errors.append(
                    f"etiqueta Quarto duplicada {label}: "
                    f"{first_source}:{first_line} y {relpath}:{line}"
                )
            else:
                native_labels[label] = (relpath, line)
        front_matter = FRONT_MATTER_RE.match(source)
        if front_matter and PAES_NUMBER_RE.search(front_matter.group("yaml")):
            yaml = front_matter.group("yaml")
            tag_match = KNOWLEDGE_TAG_RE.search(yaml)
            title_match = TITLE_RE.search(yaml)
            if not tag_match:
                errors.append(f"{relpath}: falta knowledge-tag para la pregunta PAES")
            if not title_match:
                errors.append(f"{relpath}: falta title para la pregunta PAES")
            if tag_match and title_match:
                tag = tag_match.group(1)
                objects.append({
                    "tag": tag, "type": "pregunta", "title": title_match.group(1),
                    "source": relpath, "line": 1,
                    "href": f"../{relpath}#tag-{tag}", "relations": {},
                })
            continue

        for lineno, line in enumerate(source.splitlines(), 1):
            match = OPEN_RE.match(line)
            if not match:
                continue
            classes, attrs = parse_attributes(match.group(1))
            environment_tag = attrs.get("data_environment_tag")
            if environment_tag:
                if not TAG_RE.fullmatch(environment_tag):
                    errors.append(f"{relpath}:{lineno}: identificador de entorno inválido {environment_tag!r}")
                if environment_tag in environment_tags:
                    errors.append(f"{relpath}:{lineno}: identificador de entorno duplicado {environment_tag}")
                environment_tags[environment_tag] = (relpath, lineno)
                # El entorno principal conserva el tag ya registrado del objeto.
                if not any(obj["tag"] == environment_tag for obj in objects):
                    parent = next((obj for obj in reversed(objects) if obj["source"] == relpath and obj["type"] != "ejemplo"), None)
                    objects.append({
                        "tag": environment_tag,
                        "type": "ejemplo" if attrs.get("id", "").startswith("exm-") else "entorno",
                        "title": "Ejemplo: " + parent["title"] if parent else attrs.get("id", environment_tag),
                        "source": relpath, "line": lineno,
                        "href": f"../{relpath}#{attrs['id']}",
                        "relations": {"aplica": [parent["tag"]]} if parent else {},
                    })
            if "knowledge-object" not in classes:
                continue
            tag = attrs.get("tag", "")
            if not TAG_RE.fullmatch(tag):
                errors.append(f"{relpath}:{lineno}: tag inválido {tag!r}; use 4 caracteres [0-9A-Z]")
            if attrs.get("id") != f"tag-{tag}":
                errors.append(f"{relpath}:{lineno}: el id debe ser #tag-{tag}")
            if not attrs.get("type") or not attrs.get("title"):
                errors.append(f"{relpath}:{lineno}: faltan type o title")
            if relpath in ENRICHED_CHAPTERS and tag:
                prefix = "def" if tag in DEFINITION_REPRESENTATIONS else ENV_PREFIX.get(attrs.get("type", ""), "concept")
                concept_label = f"#{prefix}-{tag}"
                example_label = f"#exm-{tag}"
                if source.count(concept_label) != 1:
                    errors.append(f"{relpath}:{lineno}: falta el entorno conceptual {concept_label}")
                if source.count(example_label) != 1:
                    errors.append(f"{relpath}:{lineno}: falta el ejemplo etiquetado {example_label}")
            relations: dict[str, list[str]] = {}
            for relation in RELATIONS:
                if attrs.get(relation):
                    relations[relation] = [x.strip() for x in attrs[relation].split(",") if x.strip()]
            objects.append(
                {
                    "tag": tag,
                    "type": attrs.get("type", ""),
                    "title": attrs.get("title", ""),
                    "source": relpath,
                    "line": lineno,
                    "href": f"../{relpath}#tag-{tag}",
                    "relations": relations,
                }
            )
    return objects, errors


def next_tag(used: set[str]) -> str:
    """Devuelve el primer identificador libre en orden base 36, desde 0000."""
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for number in range(36 ** 4):
        value = number
        code = ""
        for _ in range(4):
            value, remainder = divmod(value, 36)
            code = digits[remainder] + code
        if code not in used:
            return code
    raise ValueError("Se agotaron los identificadores de cuatro caracteres")


def main() -> int:
    objects, errors = discover()
    by_tag: dict[str, dict] = {}
    for obj in objects:
        tag = obj["tag"]
        if tag in by_tag:
            first = by_tag[tag]
            errors.append(
                f"tag duplicado {tag}: {first['source']}:{first['line']} y {obj['source']}:{obj['line']}"
            )
        else:
            by_tag[tag] = obj

    backlinks: dict[str, list[dict]] = defaultdict(list)
    for obj in objects:
        for relation, targets in obj["relations"].items():
            for target in targets:
                if not TAG_RE.fullmatch(target):
                    errors.append(f"{obj['source']}:{obj['line']}: referencia inválida {target!r}")
                elif target not in by_tag:
                    errors.append(f"{obj['source']}:{obj['line']}: referencia rota a {target}")
                else:
                    target_obj = by_tag[target]
                    from_dir = posixpath.dirname(target_obj["source"])
                    relative_source = posixpath.relpath(obj["source"], start=from_dir or ".")
                    backlinks[target].append(
                        {
                            "tag": obj["tag"],
                            "title": obj["title"],
                            "source": obj["source"],
                            "href": f"{relative_source}#{obj['href'].split('#', 1)[1]}",
                            "relation": relation,
                        }
                    )

    valid_tags = {tag for tag in by_tag if TAG_RE.fullmatch(tag)}
    if valid_tags and len(valid_tags) < 36 ** 4:
        first_free = next_tag(valid_tags)
        if int(first_free, 36) < max(int(tag, 36) for tag in valid_tags):
            errors.append(f"secuencia de identificadores con saltos: falta {first_free}; use el primer código libre")

    if errors:
        print("\n".join(f"ERROR: {message}" for message in errors), file=sys.stderr)
        return 1

    if "--next-tag" in sys.argv[1:]:
        print(next_tag(set(by_tag)))
        return 0

    GENERATED.mkdir(exist_ok=True)
    registry = {"objects": objects, "backlinks": backlinks}
    (GENERATED / "registry.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = ["---", 'title: "Catálogo de objetos"', "---", "", "Este índice se genera automáticamente.", ""]
    for obj in sorted(objects, key=lambda item: (item["type"], item["tag"])):
        lines.append(f"- `{obj['tag']}` · **{obj['type']}** · [{obj['title']}]({obj['href']})")
    (GENERATED / "catalogo.qmd").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Registro válido: {len(objects)} objetos, {sum(len(v) for v in backlinks.values())} relaciones.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
