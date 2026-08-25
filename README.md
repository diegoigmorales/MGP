# Matemática para Gañanes y Patanes

**Matemática y conocimiento profesional para la enseñanza**

MGP es una obra abierta de referencia para profesores de matemática. Su objetivo es organizar, desarrollar y conectar conocimiento matemático, didáctico, curricular, evaluativo y metodológico para facilitar su consulta, recuperación y profundización profesional.

No es un preuniversitario, un repositorio de ejercicios ni un manual exclusivamente didáctico. Las preguntas PAES y otros conjuntos de objetos forman colecciones vinculadas con contenidos y capítulos profesionales.

El proyecto avanza hacia una [arquitectura maestra de cinco partes y 102 capítulos](docs/tabla-contenidos-maestra.md). Esa estructura representa el horizonte editorial; la navegación pública numera únicamente el contenido publicado. Consulta la [organización editorial](docs/organizacion-editorial.md) y la página [Sobre MGP](acerca.qmd).

## Desarrollo local

Requisitos: Python 3.11 o superior, [Quarto](https://quarto.org/docs/get-started/) y R con los paquetes `knitr` y `rmarkdown`.

~~~powershell
python scripts/build_registry.py
python scripts/math_notation.py --check
quarto preview
~~~

La validación y el catálogo se ejecutan también como paso previo de cada render.

Las convenciones para delimitadores, números, magnitudes, unidades, porcentajes y moneda se documentan en [Convenciones de notación matemática](docs/convenciones-notacion-matematica.md). Las macros compartidas funcionan en HTML/MathJax y PDF sin depender de `siunitx`.

## Crear un objeto

Un archivo QMD puede contener uno o más objetos:

~~~markdown
::: {.knowledge-object #tag-00AF tag="00AF" type="teorema" title="Nombre" requiere="0001,0002"}
## Nombre

Contenido del objeto.
:::
~~~

Las relaciones admitidas incluyen usa, requiere, demuestra, generaliza, especializa, relacionado, error_asociado, alternativa, prerequisito, pertenece_a, evalua, profundiza, aplica y similar_a.

Los identificadores tienen cuatro caracteres en mayúsculas (0-9, A-Z). Una vez asignados, no se renombran ni reutilizan.

## Publicación

El sitio se publica con Quarto y GitHub Pages. Para producir PDF se necesita una distribución TeX compatible, por ejemplo TinyTeX:

~~~powershell
quarto render --profile book --to pdf
~~~
