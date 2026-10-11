# Convenciones de notación matemática

## Delimitadores

- Matemática en línea en QMD: `$...$`.
- Matemática desplegada en QMD: `$$...$$`, sin líneas en blanco interiores.
- No usar `\(...\)` ni `\[...\]` en QMD.
- En fuentes TeX autónomas se conservan los delimitadores propios de LaTeX.

## Conjuntos numéricos

En MGP los naturales comienzan en uno: `$\mathbb N=\{1,2,3,\ldots\}$`. El cero no es natural. La notación auxiliar `$\mathbb N_0=\mathbb N\cup\{0\}$` designa los enteros no negativos; se utiliza, por ejemplo, para cocientes y restos de la división euclídea y para exponentes que pueden ser cero. Las propiedades operatorias del cero y los resultados nulos o negativos de la sustracción se desarrollan en el capítulo de números enteros.

## Números, magnitudes y unidades

Se emplea LaTeX estándar de forma explícita. No se crean comandos propios salvo solicitud expresa.

| Propósito | Escritura | Resultado esperado |
|---|---|---|
| número con millares | `$40\,000$` | separador fino de millares |
| unidad aislada | `$\mathrm{km\,h^{-1}}$` | unidad en redonda |
| cantidad | `$3.7\,\mathrm{m\,s^{-2}}$` | espacio fino entre número y unidad |
| porcentaje | `$25\,\%$` | espacio fino antes de `%` |
| pesos chilenos | `$\$40\,000$` | signo monetario antepuesto |

Se usa punto decimal en español e inglés: `3.7`. Los números menores que uno llevan cero inicial: `0.125`. Se conservan los ceros finales que comunican precisión: `1.20`.

Los millares se separan con espacio fino (`\,`) desde cinco cifras: `12\,345\,678`; los números de cuatro cifras se escriben sin agrupación: `1234`. No se usan comas ni puntos para agrupar millares.

La notación científica usa punto centrado: `$1.25\cdot10^{-4}$`; `\dot` es un acento, no un signo de multiplicación. El signo menos se escribe dentro de matemática: `$-2.75$`.

Las unidades compuestas se escriben como productos con exponentes negativos: `$\mathrm{kg\,m^{-3}}$`, `$\mathrm{m\,s^{-2}}$` y `$\mathrm{km\,h^{-1}}$`. Las fracciones que explican factores de conversión se conservan, pues muestran razones de cantidades, no un símbolo de unidad compuesto.

Las variables permanecen en cursiva matemática; los símbolos de unidades van en redonda con `\mathrm{}`, sin plural ni punto de abreviatura. Los operadores convencionales se escriben con `\sin`, `\cos`, `\ln`, `\log` y `\det`; los nombres adicionales usan `\operatorname{}`. Entre valor y unidad y antes de `%` se inserta `\,`. Para grados Celsius: `$20\,{}^\circ\mathrm{C}$`; los ángulos planos conservan `$30^\circ$`.

Estas convenciones toman el SI como base. El punto decimal, la agrupación desde cinco cifras y las potencias negativas son decisiones editoriales adoptadas entre las opciones admitidas.

## Aplicación en Quarto

No se carga `siunitx` ni se usan `\num`, `\qty` o `\unit` en las páginas: se escribe su resultado con TeX estándar, que comprende MathJax. Por ejemplo:

~~~markdown
$3.14159$
$1\,234\,567.89$
$1.25\cdot10^{-4}$
$25\,\mathrm{kg}$
$9.81\,\mathrm{m\,s^{-2}}$
$80\,\mathrm{km\,h^{-1}}$
$25\,\%$
~~~

`scripts/math_notation.py --write` normaliza las fuentes existentes y `--check` valida la convención antes de cada render. En QMD, la transformación preserva metadatos, código, enlaces y comas que separan coordenadas, argumentos o elementos de conjuntos. En los fragmentos TeX de PAES también se normalizan las cantidades que aparecen sin delimitadores matemáticos. Los rótulos originales de imágenes externas conservan la escritura de la fuente; las figuras originales generadas por el proyecto usan estas convenciones.

## Distribuciones de probabilidad

Los nombres de distribuciones se escriben directamente en redonda porque su frecuencia no justifica una macro específica. Por ejemplo:

- normal: `$X\sim\operatorname{N}(\mu,\sigma^2)$`;
- binomial: `$X\sim\operatorname{Binomial}(n,p)$`;
- Poisson: `$X\sim\operatorname{Poisson}(\lambda)$`;
- uniforme: `$X\sim\operatorname{Uniforme}(a,b)$`.

La misma convención se aplica a otras distribuciones: `\operatorname{Bernoulli}`, `\operatorname{Geométrica}`, `\operatorname{Hipergeométrica}`, `\operatorname{Multinomial}` y `\operatorname{Exponencial}`. No se crean comandos como `\Normal` o `\Binomial` y tampoco se emplean `\mathcal{N}` ni `\mathrm{Binomial}`.

## Compatibilidad

La notación utiliza únicamente construcciones TeX comprendidas directamente por MathJax y LaTeX. No depende de macros locales ni de `siunitx`, de modo que el mismo contenido puede publicarse en GitHub Pages y compilarse como PDF.
