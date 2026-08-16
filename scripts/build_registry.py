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
OPEN_RE = re.compile(r"^\s*:::\s*\{([^}]*)\}\s*$")
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


def discover() -> tuple[list[dict], list[str]]:
    objects: list[dict] = []
    errors: list[str] = []
    ignored = {"_site", "_book", ".quarto", ".git", "_generated"}
    for path in sorted(ROOT.rglob("*.qmd")):
        if any(part in ignored for part in path.relative_to(ROOT).parts):
            continue
        relpath = path.relative_to(ROOT).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = OPEN_RE.match(line)
            if not match:
                continue
            classes, attrs = parse_attributes(match.group(1))
            if "knowledge-object" not in classes:
                continue
            tag = attrs.get("tag", "")
            if not TAG_RE.fullmatch(tag):
                errors.append(f"{relpath}:{lineno}: tag inválido {tag!r}; use 4 caracteres [0-9A-Z]")
            if attrs.get("id") != f"tag-{tag}":
                errors.append(f"{relpath}:{lineno}: el id debe ser #tag-{tag}")
            if not attrs.get("type") or not attrs.get("title"):
                errors.append(f"{relpath}:{lineno}: faltan type o title")
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
                            "href": f"{relative_source}#tag-{obj['tag']}",
                            "relation": relation,
                        }
                    )

    if errors:
        print("\n".join(f"ERROR: {message}" for message in errors), file=sys.stderr)
        return 1

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
