# Matemática para Gañanes y Patanes

Base de conocimiento abierta e interconectada para la preparación de la PAES de Matemática, publicada con Quarto.

## Desarrollo local

Requisitos: Python 3.11 o superior y [Quarto](https://quarto.org/docs/get-started/).

```powershell
python scripts/build_registry.py
quarto preview
```

La validación y el catálogo se ejecutan también como paso previo de cada render.

## Crear un objeto

Un archivo `.qmd` puede contener uno o más objetos:

```markdown
::: {.knowledge-object #tag-00AF tag="00AF" type="teorema" title="Nombre" requiere="0001,0002"}
## Nombre

Contenido del objeto.
:::
```

Relaciones admitidas: `usa`, `requiere`, `demuestra`, `generaliza`, `especializa`, `relacionado`, `error_asociado`, `alternativa` y `prerequisito`.

Los tags tienen cuatro caracteres en mayúsculas (`0-9`, `A-Z`). Una vez asignados, no se renombran ni reutilizan. Antes de publicar, el script detecta tags inválidos o duplicados y referencias rotas.

## Publicación

1. Cambiar `USUARIO` y `mgp` en `_quarto.yml` por la cuenta y repositorio reales.
2. Crear un repositorio en GitHub y subir la rama `main`.
3. En **Settings → Pages → Build and deployment**, seleccionar **GitHub Actions**.
4. Cada push a `main` validará y publicará el sitio.

Para producir PDF se necesita una distribución TeX compatible con TikZ/pgfplots (por ejemplo, TinyTeX):

```powershell
quarto render --to pdf
```

