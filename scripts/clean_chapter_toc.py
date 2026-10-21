"""Retira del TOC HTML los encabezados auxiliares de numeración."""
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parents[1]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


@dataclass
class Node:
    tag: str
    start: int
    open_end: int
    close_start: int = 0
    end: int = 0
    children: list = field(default_factory=list)
    toc: bool = False
    marker: bool = False


class TocParser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0]
        for i, char in enumerate(source):
            if char == "\n":
                self.lines.append(i + 1)
        self.root = Node("root", 0, 0, len(source), len(source))
        self.stack = [self.root]

    def position(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        start = self.position()
        node = Node(tag, start, start + len(self.get_starttag_text()))
        node.toc = self.stack[-1].toc or (tag == "nav" and attrs.get("id") == "TOC")
        self.stack[-1].children.append(node)
        if node.toc and tag == "a" and any(
            attrs.get(key, "").startswith(prefix)
            for key, prefix in (("href", "#mgp-chapter"), ("data-scroll-target", "#mgp-chapter"), ("id", "toc-mgp-chapter"))
        ):
            for ancestor in reversed(self.stack):
                if ancestor.tag == "li":
                    ancestor.marker = True
                    break
        if tag in VOID:
            node.close_start = node.end = node.open_end
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node = self.stack.pop()
            node.close_start = node.end = node.open_end

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                node = self.stack[i]
                node.close_start = self.position()
                node.end = self.source.index(">", node.close_start) + 1
                self.stack = self.stack[:i]
                break


def clean_toc(document):
    match = re.search(r"<nav\b[^>]*\bid=[\"']TOC[\"'][^>]*>.*?</nav>", document, re.S)
    if not match:
        return document
    source = match[0]
    parser = TocParser(source)
    parser.feed(source)

    def contents(node):
        parts = []
        cursor = node.open_end
        for child in node.children:
            parts.extend((source[cursor:child.start], render(child)))
            cursor = child.end
        parts.append(source[cursor:node.close_start])
        return "".join(parts)

    def render(node):
        if node.marker:
            # Si Quarto anida secciones reales debajo, las eleva en el índice.
            return "".join(contents(child) for child in node.children if child.tag in {"ul", "ol"})
        return source[node.start:node.open_end] + contents(node) + source[node.close_start:node.end]

    return document[:match.start()] + contents(parser.root) + document[match.end():]


def main():
    output = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
    if not output.is_absolute():
        output = ROOT / output
    changed = 0
    for path in output.rglob("*.html"):
        source = path.read_text(encoding="utf-8")
        if 'toc-mgp-chapter' not in source:
            continue
        cleaned = clean_toc(source)
        if cleaned != source:
            path.write_text(cleaned, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Índices de capítulo depurados: {changed} páginas.")


if __name__ == "__main__":
    main()
