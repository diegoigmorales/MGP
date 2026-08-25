# Organización editorial del proyecto

MGP posee una arquitectura maestra de cinco partes y 102 capítulos como horizonte editorial. La navegación pública muestra y numera consecutivamente sólo el contenido desarrollado.

## Jerarquía editorial

1. Parte.
2. Capítulo.
3. Sección.
4. Subsección.
5. Objeto de conocimiento.

La numeración pública de partes y capítulos es provisional y depende del contenido publicado. La numeración de la tabla maestra expresa la arquitectura objetivo y no se traslada automáticamente al sitio. Cada objeto reutilizable posee un identificador permanente independiente; su ubicación puede cambiar sin modificar ese identificador.

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
