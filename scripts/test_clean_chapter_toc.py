import unittest
from clean_chapter_toc import clean_toc


class CleanChapterTocTests(unittest.TestCase):
    def test_remove_complete_entry_and_preserve_page(self):
        entry = '<li><a href="#mgp-chapter-1"><span>12</span> Capítulo 12. Funciones</a></li>'
        section = '<li><a href="#funciones">12.1 Propósito y alcance</a></li>'
        before = '<h1>Capítulo 12. Funciones</h1><nav id="TOC"><ul>'
        after = '</ul></nav><section id="mgp-chapter-1"><p>Contenido</p></section>'
        self.assertEqual(clean_toc(before + entry + section + after), before + section + after)

    def test_nested_sections_and_legacy_anchor(self):
        real = '<li><a href="#seccion">6.1 Sección</a></li>'
        source = '<nav id="TOC"><ul><li><a href="#mgp-chapter">Capítulo</a><ul><li><a href="#mgp-chapter-2">Auxiliar</a><ul>' + real + '</ul></li></ul></li></ul></nav>'
        expected = '<nav id="TOC"><ul>' + real + '</ul></nav>'
        self.assertEqual(clean_toc(source), expected)

    def test_no_index_and_idempotence(self):
        source = '<h1>Capítulo</h1><nav id="TOC"><ul><li><a href="#seccion">Sección</a></li></ul></nav>'
        self.assertEqual(clean_toc(source), source)
        self.assertEqual(clean_toc(clean_toc(source)), source)
        self.assertEqual(clean_toc('<h1>Capítulo</h1>'), '<h1>Capítulo</h1>')


if __name__ == "__main__":
    unittest.main()
