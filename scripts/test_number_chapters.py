"""Verifica sincronización e inserción de capítulos en un proyecto temporal."""
import contextlib
import io
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
import yaml
from number_chapters import synchronize


class VisibleHeadings(HTMLParser):
    def __init__(self, depth=1):
        super().__init__()
        self.depth = depth
        self.stack = []
        self.hidden_sections = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"h2", "h3", "h4", "h5", "h6"} and len(attrs.get("data-number", "").split(".")) > self.depth:
            if any("mgp-chapter-anchor" in a.get("class", "") or a.get("aria-hidden") == "true"
                   for _, a in self.stack):
                self.hidden_sections.append(attrs["data-number"])
        if tag not in {"meta", "link", "img", "input", "br", "hr", "source", "wbr", "area", "base", "col", "embed", "param", "track"}:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.stack = self.stack[:i]
                break


class NumberChaptersTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mgp-numbering-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "filters").mkdir()
        shutil.copy(Path(__file__).resolve().parents[1] / "filters/chapter-numbering.lua",
                    self.root / "filters/chapter-numbering.lua")
        config = {"project": {"type": "website"}, "website": {"sidebar": {"contents": []}},
                  "format": {"html": {"toc": True, "filters": ["filters/chapter-numbering.lua"]}}}
        (self.root / "_quarto.yml").write_text(yaml.safe_dump(config), encoding="utf-8")
        for name in ["index", "acerca", "part"]:
            (self.root / f"{name}.qmd").write_text(f"---\ntitle: {name}\n---\n\n# {name} {{.unnumbered}}\n", encoding="utf-8")
        for n in range(1, 7):
            (self.root / f"c{n}.qmd").write_text(
                f"---\ntitle: Capítulo {n}. Tema {n}\n---\n\n## Sección\n\nTexto.\n\n### Subsección\n\nTexto.\n\n#### Apartado\n\nTexto.\n", encoding="utf-8")
        chapter = self.root / "c6.qmd"
        chapter.write_text(chapter.read_text(encoding="utf-8").replace(
            "Texto.\n\n###", "[Ampliación](linked.qmd)\n\n###", 1), encoding="utf-8")
        (self.root / "linked.qmd").write_text(
            "---\ntoc: true\n---\n\n# 6.1 Ampliación {.unnumbered}\n\n## 6.1.1 Detalle\n\nTexto.\n", encoding="utf-8")
        linked = self.root / "linked.qmd"
        linked.write_text(linked.read_text(encoding="utf-8") + "\n[Detalle](detail.qmd)\n", encoding="utf-8")
        (self.root / "detail.qmd").write_text(
            "---\ntoc: true\n---\n\n# 6.1.1 Detalle {.unnumbered}\n\n## Interior\n", encoding="utf-8")
        self.entries = [f"c{n}.qmd" for n in range(1, 7)]
        self.write_book()

    def write_book(self):
        book = {"book": {"chapters": ["index.qmd", "acerca.qmd", {"part": "part.qmd", "chapters": self.entries}]}}
        (self.root / "_quarto-book.yml").write_text(yaml.safe_dump(book), encoding="utf-8")

    def sync(self):
        with contextlib.redirect_stdout(io.StringIO()):
            synchronize(self.root)

    def test_insert_and_idempotence(self):
        self.sync()
        content = (self.root / "c6.qmd").read_text(encoding="utf-8")
        self.sync()
        self.assertEqual(content, (self.root / "c6.qmd").read_text(encoding="utf-8"))
        self.insert()
        meta = yaml.safe_load((self.root / "c6.qmd").read_text(encoding="utf-8").split("---")[1])
        self.assertEqual(meta["title"], "Tema 6")
        self.assertEqual(meta["format"]["html"]["title"], "Capítulo 7. Tema 6")
        self.assertEqual(meta["format"]["html"]["number-offset"][0], 6)
        self.assertNotIn("number-offset", meta.get("format", {}).get("pdf", {}))
        self.assertIn("Capítulo 7. Tema 6", (self.root / "_quarto.yml").read_text(encoding="utf-8"))

    def test_linked_section_follows_heading_position(self):
        self.sync()
        path = self.root / "c6.qmd"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "## Sección", "## Nueva sección\n\nTexto.\n\n## Sección", 1), encoding="utf-8")
        self.sync()
        meta = yaml.safe_load((self.root / "linked.qmd").read_text(encoding="utf-8").split("---")[1])
        self.assertEqual(meta["format"]["html"]["title"], "6.2 Ampliación")

    def insert(self):
        (self.root / "nuevo.qmd").write_text("---\ntitle: Nuevo\n---\n\n## Inicio\n", encoding="utf-8")
        self.entries.insert(0, "nuevo.qmd")
        self.write_book()
        self.sync()

    @unittest.skipUnless(shutil.which("quarto"), "requiere Quarto")
    def test_rendered_numbers_follow_insert(self):
        self.sync()
        for expected in [6, 7]:
            if expected == 7:
                self.insert()
            result = subprocess.run([shutil.which("quarto"), "render", "c6.qmd", "--to", "html"],
                                    cwd=self.root, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = (self.root / "_site/c6.html").read_text(encoding="utf-8")
            for number in [f"{expected}.1", f"{expected}.1.1", f"{expected}.1.1.1"]:
                self.assertIn(f'data-number="{number}"', html)
                self.assertRegex(html, rf'header-section-number">{re.escape(number)}</span>')
            self.assertIn(f"Capítulo {expected}. Tema 6", html)
            headings = VisibleHeadings()
            headings.feed(html)
            self.assertEqual(headings.hidden_sections, [])
            linked = subprocess.run([shutil.which("quarto"), "render", "linked.qmd", "--to", "html"],
                                    cwd=self.root, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(linked.returncode, 0, linked.stdout + linked.stderr)
            linked_html = (self.root / "_site/linked.html").read_text(encoding="utf-8")
            self.assertIn(f'data-number="{expected}.1.1"', linked_html)
            self.assertIn(f"{expected}.1 Ampliación", linked_html)
            headings = VisibleHeadings(depth=2)
            headings.feed(linked_html)
            self.assertEqual(headings.hidden_sections, [])
            detail = subprocess.run([shutil.which("quarto"), "render", "detail.qmd", "--to", "html"],
                                    cwd=self.root, capture_output=True, text=True, encoding="utf-8", errors="replace")
            self.assertEqual(detail.returncode, 0, detail.stdout + detail.stderr)
            detail_html = (self.root / "_site/detail.html").read_text(encoding="utf-8")
            self.assertIn(f'data-number="{expected}.1.1.1"', detail_html)


if __name__ == "__main__":
    unittest.main()
