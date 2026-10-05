# Organización editorial del proyecto

MGP posee una arquitectura maestra de cinco partes y 102 capítulos como horizonte editorial. La navegación pública muestra sólo el contenido desarrollado, en el orden de la tabla maestra y con numeración consecutiva provisional.

## Jerarquía editorial

1. Parte.
2. Capítulo.
3. Sección.
4. Subsección.
5. Objeto de conocimiento.

El orden de las partes y capítulos publicados sigue la tabla maestra. La numeración pública de partes y capítulos es consecutiva y provisional: se omite el material pendiente sin dejar saltos. Al incorporar capítulos intermedios, se ajustan los números públicos. La numeración maestra identifica la ubicación editorial proyectada y se conserva como referencia independiente. Cada objeto reutilizable posee un identificador permanente independiente; su ubicación puede cambiar sin modificar ese identificador.

## Correspondencia entre capítulos publicados y maestros

Esta correspondencia registra el estado actual; los números públicos cambian al incorporar contenido. Las rutas y los identificadores de objetos se conservan.

| Capítulo público | Capítulo maestro | Contenido |
|---:|---:|---|
| 1 | 33 | Porcentajes |
| 2 | 34 | Potencias, raíces y logaritmos |
| 3 | 35 | Álgebra elemental |
| 4 | 36 | Ecuaciones e inecuaciones |
| 5 | 37 | Sucesiones y series elementales |
| 6 | 38 | Funciones |
| 7 | 44 | Combinatoria y probabilidad |
| 8 | 45 | Estadística escolar |
| 9 | 74 | Sistema curricular chileno |
| 10 | 75 | PAES de Matemática |

## Capítulos, colecciones e índices

Un capítulo desarrolla un cuerpo de conocimiento, una metodología o un sistema institucional estable y autónomo. Las preguntas PAES, M1, M2 y otras evaluaciones son objetos agrupados en colecciones: no constituyen capítulos. Los índices y vistas sirven para recuperar capítulos u objetos, pero tampoco amplían la arquitectura maestra.

## Ubicación del contenido

- Matemática escolar: contenidos/libro/.
- Fundamentos universitarios y aplicaciones: contenidos/universitario/.
- Currículo y evaluación: contenidos/curriculum/ y contenidos/paes/.
- Colecciones PAES: contenidos/paes/<prueba>/.
- Infraestructura editorial compartida: filters/, scripts/ y _generated/.

## Publicación progresiva

La tabla maestra se conserva en docs/tabla-contenidos-maestra.md. La existencia de un capítulo en ella no implica que esté desarrollado ni publicado, y no obliga a crear páginas vacías. La navegación pública incorpora cada capítulo cuando dispone de contenido utilizable.

## Procedencia

Los objetos originales se identifican como tales. Todo material externo debe declarar autor, título, fuente, enlace, año, titular de derechos, alcance de la transcripción y fundamento de uso.
