"""Regresiones para normalizar notación sin cambiar significado matemático."""
import unittest
from math_notation import format_number, normalize_math, normalize_qmd, normalize_tex


class SINotationTests(unittest.TestCase):
    def test_numbers_and_precision(self):
        for raw, expected in [
            ('1234', '1234'), (r'1\,234', '1234'),
            ('12345678', r'12\,345\,678'),
            ('1234567.89', r'1\,234\,567.89'),
            ('0.00450', '0.00450'), ('.125', '0.125'),
            ('-2.75', '-2.75'), ('1.20', '1.20'),
            ('1.25e-4', r'1.25\cdot10^{-4}'),
        ]:
            with self.subTest(raw=raw):
                self.assertEqual(format_number(raw), expected)

    def test_decimal_after_command_and_repeating_decimal(self):
        self.assertEqual(normalize_math(r'6\cdot8{,}5=51'), r'6\cdot8.5=51')
        self.assertEqual(normalize_math(r'0{,}\overline3'), r'0.\overline3')
        self.assertEqual(normalize_math(r'0{,}3\,456'), '0.3456')

    def test_quantities_and_scientific_notation(self):
        self.assertEqual(normalize_math(r'9{,}81\mathrm{m/s^{2}}'),
                         r'9.81\,\mathrm{m\,s^{-2}}')
        self.assertEqual(normalize_math(r'\mathrm{kg/m^3}'), r'\mathrm{kg\,m^{-3}}')
        self.assertEqual(normalize_math(r'\mathrm{m^3/h}'), r'\mathrm{m^{3}\,h^{-1}}')
        self.assertEqual(normalize_math(r'25\%+p\%'), r'25\,\%+p\,\%')
        self.assertEqual(normalize_math(r'1.25\times10^{-4}'), r'1.25\cdot10^{-4}')

    def test_numeric_coefficients(self):
        self.assertEqual(normalize_math('150000x + 100000'), r'150\,000x + 100\,000')

    def test_lists_arguments_and_conversion_fractions(self):
        text = r'\{1,2,3\};(1,800);\operatorname{N}(170,6^2);\frac{1\,\mathrm{h}}{60\,\mathrm{min}}'
        self.assertEqual(normalize_math(text), text)

    def test_qmd_protects_metadata_code_and_links(self):
        protected = '---\ntitle: "2027"\n---\n`$12345$`\n```tex\n$3{,}7$\n```\n[Fuente](https://example.org/12345)\n'
        self.assertEqual(normalize_qmd(protected + r'$3{,}7$'), protected + '$3.7$')

    def test_tex_fragments_and_idempotence(self):
        raw = r'Valor 3{,}7\,\mathrm{m/s^2}; $1\,000$ y $25\%$'
        expected = r'Valor 3.7\,\mathrm{m\,s^{-2}}; $1000$ y $25\,\%$'
        self.assertEqual(normalize_tex(raw), expected)
        self.assertEqual(normalize_tex(expected), expected)
        qmd = r'$1\,234\,567.89$; $0.00450$; $80\,\mathrm{km\,h^{-1}}$'
        self.assertEqual(normalize_qmd(qmd), qmd)


if __name__ == '__main__':
    unittest.main()
