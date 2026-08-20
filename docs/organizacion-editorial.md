# Organización editorial del proyecto

La plataforma tiene tres recorridos: preparación PAES, libro de matemática y profundización universitaria. No son bases separadas: comparten tags, objetos, referencias y backlinks.

## Jerarquía editorial

La jerarquía de lectura es:

1. Parte.
2. Capítulo.
3. Sección.
4. Subsección.
5. Objeto de conocimiento.

Un objeto puede ocupar una sección completa o aparecer junto a otros objetos dentro de ella. La jerarquía editorial puede cambiar; el tag del objeto no.

### Numeración editorial

La numeración se escribe como parte del encabezado cuando tiene valor editorial: `Parte I · Números`, `Capítulo 1 · Razones y porcentajes`, `Sección 2.1 · Porcentajes` o `Pregunta 20`. Quarto no agrega numeración automática a los encabezados HTML, para evitar fórmulas redundantes como `1 Parte I` o `1 Pregunta 20`.

## Ubicación de contenido nuevo

- Pregunta PAES oficial: `contenidos/paes/<prueba>/preguntas-oficiales/`.
- Pregunta original: `contenidos/paes/<prueba>/preguntas-originales/`.
- Teoría escolar o general: `contenidos/libro/<materia>/`.
- Contenido o problema universitario: `contenidos/universitario/<asignatura>/`.
- Materia, eje, habilidad u objetivo curricular: `contenidos/curriculum/`.

## Profundidad

La página PAES muestra primero la respuesta y permite desplegar métodos y distractores. El libro desarrolla la teoría de manera narrativa. La sección universitaria declara prerrequisitos y enlaza hacia los fundamentos escolares.

## Procedencia

Los problemas originales se identifican como tales. Todo material externo debe declarar autor, título, fuente, enlace, año, titular de derechos, alcance de la transcripción y fundamento de uso.

## Publicación progresiva y PDF

La tabla de contenidos maestra se conserva en `docs/` como hoja de ruta interna. La navegación pública solo incluye páginas con contenido utilizable; los recorridos, capítulos y niveles futuros permanecen en el repositorio hasta que estén listos para publicación.

El enlace PDF se habilita de forma explícita para libros completos, capítulos, guías y colecciones que tengan un PDF generado en el flujo de publicación. Se deshabilita en preguntas individuales, índices breves, páginas administrativas y páginas acerca del proyecto.

