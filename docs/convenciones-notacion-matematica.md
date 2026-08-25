# Convenciones de notación matemática

## Delimitadores

- Matemática en línea en QMD: `$...$`.
- Matemática desplegada en QMD: `$$...$$`, sin líneas en blanco interiores.
- No usar `\(...\)` ni `\[...\]` en QMD.
- En fuentes TeX autónomas se conservan los delimitadores propios de LaTeX.

## Números, magnitudes y unidades

Se emplea LaTeX estándar de forma explícita. No se crean comandos propios salvo solicitud expresa.

| Propósito | Escritura | Resultado esperado |
|---|---|---|
| número con millares | `$40\,000$` | separador fino de millares |
| unidad aislada | `$\mathrm{km/h}$` | unidad en redonda |
| cantidad | `$3{,}7\,\mathrm{m/s^2}$` | espacio fino entre número y unidad |
| porcentaje | `$25\,\%$` | espacio fino antes de `%` |
| pesos chilenos | `$\$40\,000$` | signo monetario antepuesto |

Se usa coma decimal: `3{,}7`. Los millares se agrupan manualmente con `\,`: `100\,000`. Las variables permanecen en cursiva matemática y los nombres de unidades se escriben en redonda mediante `\mathrm{}`. Entre una cantidad y su unidad se inserta `\,`.

## Distribuciones de probabilidad

Los nombres de distribuciones se escriben directamente en redonda porque su frecuencia no justifica una macro específica. Por ejemplo:

- normal: `$X\sim\operatorname{N}(\mu,\sigma^2)$`;
- binomial: `$X\sim\operatorname{Binomial}(n,p)$`;
- Poisson: `$X\sim\operatorname{Poisson}(\lambda)$`;
- uniforme: `$X\sim\operatorname{Uniforme}(a,b)$`.

La misma convención se aplica a otras distribuciones: `\operatorname{Bernoulli}`, `\operatorname{Geométrica}`, `\operatorname{Hipergeométrica}`, `\operatorname{Multinomial}` y `\operatorname{Exponencial}`. No se crean comandos como `\Normal` o `\Binomial` y tampoco se emplean `\mathcal{N}` ni `\mathrm{Binomial}`.

## Compatibilidad

La notación utiliza únicamente construcciones TeX comprendidas directamente por MathJax y LaTeX. No depende de macros locales ni de `siunitx`, de modo que el mismo contenido puede publicarse en GitHub Pages y compilarse como PDF.
