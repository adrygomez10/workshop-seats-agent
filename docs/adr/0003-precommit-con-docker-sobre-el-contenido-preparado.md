# 0003. Precommit con Docker sobre el contenido preparado

## Estado

Aceptada.

## Contexto

El proyecto fija Python 3.15.2. `pre-commit` depende de `pyyaml`, que no
publica paquetes precompilados de esa versión para Windows. Sin un
compilador de C, `uv sync` falla en Windows y el hook no se puede instalar
desde GitHub Desktop ni desde Git para Windows.

El hook debe comprobar el contenido que se va a guardar, no los cambios
pendientes de la copia de trabajo.

## Decisión

- El hook versionado `.githooks/pre-commit` copia el contenido preparado con
  `git checkout-index` a una carpeta temporal y construye allí la etapa
  `quality` del `Dockerfile`.
- Esa etapa instala las dependencias del lock y ejecuta
  `scripts/check_quality.py`. La CI ejecuta la misma entrada con uv y
  construye también la etapa `quality`.
- Se instala una vez por copia con `git config core.hooksPath .githooks`.
- `pre-commit` no forma parte de las dependencias de desarrollo.

## Consecuencias

- El mismo hook funciona en Windows, Linux y macOS. Solo necesita Docker.
- Un cambio sin preparar no oculta ni provoca un fallo del commit.
- La primera ejecución descarga la imagen de Python y las dependencias. Las
  siguientes reutilizan la caché de Docker mientras no cambien
  `pyproject.toml` ni `uv.lock`.
- Sin Docker, `uv run python scripts/check_quality.py` ejecuta las mismas
  comprobaciones, pero no se instala como hook.
