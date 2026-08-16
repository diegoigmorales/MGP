# Arquitectura inicial

## Fuente de verdad

Los bloques `.knowledge-object` contenidos en archivos `.qmd` son la fuente editorial. Sus atributos forman el modelo mínimo de datos. Quarto consume ese modelo, pero no lo define.

El registro `_generated/registry.json` es un artefacto reproducible: nunca se edita a mano. Puede alimentar buscadores, grafos, estadísticas, rutas de aprendizaje o una futura migración.

## Contrato de identidad

- Un tag identifica un objeto, no un archivo ni una URL.
- Formato inicial: cuatro caracteres `[0-9A-Z]`.
- Un tag publicado jamás cambia ni se reasigna.
- Si se retira un objeto, su tag debe conservarse en un futuro registro de tags retirados (pendiente para la siguiente etapa).
- La ubicación física puede cambiar; el registro vuelve a calcular los enlaces.

## Flujo de construcción

1. El autor escribe contenido y declara relaciones por tag.
2. `scripts/build_registry.py` descubre objetos, valida unicidad e integridad referencial y genera el catálogo.
3. `filters/knowledge.lua` añade el distintivo del tag y backlinks al renderizar.
4. Quarto produce HTML o PDF desde la misma fuente.
5. GitHub Actions publica HTML en GitHub Pages sólo si las validaciones pasan.

## Evolución recomendada

1. Añadir un registro versionado de tags retirados y un asignador que nunca recicle identidades.
2. Definir un vocabulario controlado de tipos y relaciones en un esquema independiente (JSON Schema).
3. Generar índices por contenido PAES, habilidad, dificultad y tipo de objeto.
4. Incorporar pruebas de enlaces del HTML y una visualización del grafo.
5. Añadir perfiles de lectura y rutas de aprendizaje derivadas, sin duplicar contenido.
6. Recién cuando el volumen lo justifique, evaluar una base de datos o un VPS; el JSON exportable mantiene abierta esa migración.

