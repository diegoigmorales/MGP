"""Sincroniza títulos, menú y numeración HTML con el orden del libro."""
from pathlib import Path
import re
from collections import deque
import yaml

ROOT = Path(__file__).resolve().parents[1]


def read_document(path):
    source = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---[^\n]*\n", source, re.S)
    if not match:
        raise ValueError(f"Falta encabezado YAML en {path}")
    return yaml.safe_load(match[1]) or {}, source[match.end():]


def write_if_changed(path, content):
    if path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8", newline="\n")


def chapter_order(entries):
    for entry in entries:
        if isinstance(entry, dict):
            yield from chapter_order(entry.get("chapters", []))
        elif entry not in {"index.qmd", "acerca.qmd"}:
            yield entry


def linked_groups(root, relative, body, candidates):
    """Agrupa páginas de sección por el encabezado que contiene sus enlaces."""
    counters = [0] * 5
    current = ()
    groups = {}
    in_code = False
    for line in body.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            in_code = not in_code
        if in_code:
            continue
        heading = re.match(r"^(#{2,6}) ", line)
        if heading:
            level = len(heading[1]) - 2
            counters[level] += 1
            counters[level + 1:] = [0] * (4 - level)
            current = tuple(counters[:level + 1])
        for link in re.findall(r"\]\(([^)\s]+\.qmd)(?:#[^)]*)?\)", line):
            target = (root / relative).parent.joinpath(link).resolve()
            try:
                target = target.relative_to(root.resolve()).as_posix()
            except ValueError:
                continue
            if target in candidates:
                group = groups.setdefault(current, [])
                if target not in group:
                    group.append(target)
    return groups


def linked_documents(root, chapters):
    documents = {}
    for path in root.rglob("*.qmd"):
        relative = path.relative_to(root)
        if any(part.startswith(".") or part.startswith("_") for part in relative.parts):
            continue
        if relative.as_posix() in chapters:
            continue
        try:
            meta, body = read_document(path)
        except ValueError:
            continue
        heading = re.search(r"^# (\d+(?:\.\d+)+)\s+(.+)$", body, re.M)
        if not heading and not meta.get("mgp-linked-section"):
            continue
        if heading:
            meta["title"] = re.sub(r"\s*\{.*?\}\s*$", "", heading[2])
            body = body[:heading.start()] + body[heading.end():]
        meta["mgp-linked-section"] = True
        documents[relative.as_posix()] = (meta, body)
    return documents


def number_document(root, relative, prefix, meta, body, chapter=False):
    title = meta.get("title")
    if title is None:
        heading = re.search(r"^# (.+)\n", body, re.M)
        if not heading:
            raise ValueError(f"Falta título en {relative}")
        title = heading[1]
        body = body[:heading.start()] + body[heading.end():]
    title = re.sub(r"^Capítulo \d+\.\s*", "", title)
    meta["title"] = title
    meta["number-sections"] = True
    meta["number-depth"] = 6
    formats = meta.setdefault("format", {})
    if not isinstance(formats, dict):
        formats = {formats: "default"} if isinstance(formats, str) else {}
        meta["format"] = formats
    html = formats.get("html")
    if not isinstance(html, dict):
        html = {}
        formats["html"] = html
    label = f"Capítulo {prefix[0]}. {title}" if chapter else ".".join(map(str, prefix)) + " " + title
    html["title"] = label
    html["number-offset"] = [value - 1 for value in prefix] + [0] * (6 - len(prefix))
    meta.pop("mgp-chapter-number", None)
    meta["mgp-number-prefix"] = ".".join(map(str, prefix))
    body = re.sub(r"^(#{2,6}) \d+(?:\.\d+)+\.?\s+", r"\1 ", body, flags=re.M)
    header = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000)
    write_if_changed(root / relative, "---\n" + header + "---\n" + body)
    return label


def synchronize(root=ROOT):
    book = yaml.safe_load((root / "_quarto-book.yml").read_text(encoding="utf-8"))["book"]
    paths = list(chapter_order(book["chapters"]))
    if len(paths) != len(set(paths)):
        raise ValueError("Un capítulo aparece más de una vez en el índice del libro")
    labels = {}
    documents = linked_documents(root, set(paths))
    prefixes = {relative: (number,) for number, relative in enumerate(paths, 1)}
    pending = deque(paths)
    while pending:
        relative = pending.popleft()
        meta, body = documents.get(relative, (None, None))
        if meta is None:
            meta, body = read_document(root / relative)
        groups = linked_groups(root, relative, body, documents)
        for heading, targets in groups.items():
            for index, target in enumerate(targets, 1):
                if target not in prefixes:
                    prefixes[target] = prefixes[relative] + heading + ((index,) if len(targets) > 1 else ())
                    pending.append(target)
        label = number_document(root, relative, prefixes[relative], meta, body, chapter=relative in paths)
        if relative in paths:
            labels[relative] = label
    missing = set(documents) - set(prefixes)
    if missing:
        raise ValueError("Páginas de sección sin enlace desde su capítulo: " + ", ".join(sorted(missing)))

    def navigation(entries):
        result = []
        for entry in entries:
            if isinstance(entry, dict):
                part_path = root / entry["part"]
                _, body = read_document(part_path)
                heading = re.search(r"^# (.+?)(?: \{.*?\})?\s*$", body, re.M)
                result.append({"section": heading[1], "href": entry["part"],
                               "contents": navigation(entry["chapters"])})
            elif entry in labels:
                result.append({"text": labels[entry], "href": entry})
            else:
                result.append({"text": "Portada" if entry == "index.qmd" else "Sobre MGP", "href": entry})
        return result

    # Los rótulos del índice publicado también se derivan de los destinos.
    index_path = root / "contenidos/index.qmd"
    if index_path.exists():
        source = index_path.read_text(encoding="utf-8")
        def target_key(link):
            return (index_path.parent / link).resolve().relative_to(root.resolve()).as_posix()
        source = re.sub(r"^(### )(Capítulo \d+\.[^\n]*)(\n\n- \[[^\]]+\]\(([^)]+)\))",
                        lambda m: m[1] + labels.get(target_key(m[4]), m[2]) + m[3], source, flags=re.M)
        source = re.sub(r"\[\d+(?:\.\d+)+ ([^\]]+)\]\(([^)]+)\)",
                        lambda m: "[" + (".".join(map(str, prefixes[target_key(m[2])])) + " " if target_key(m[2]) in prefixes else "") + m[1] + "](" + m[2] + ")",
                        source)
        write_if_changed(index_path, source)

    config_path = root / "_quarto.yml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config["website"]["sidebar"]["contents"] = navigation(book["chapters"])
    write_if_changed(config_path, yaml.safe_dump(config, allow_unicode=True, sort_keys=False, width=1000))
    print(f"Numeración sincronizada: {len(paths)} capítulos y {len(documents)} páginas de sección.")


if __name__ == "__main__":
    synchronize()
