# Workshop Seats Agent

Aplicación de consola en Python para los talleres de los artículos
[LangChain y LangGraph: organizar un flujo de IA con pasos y decisiones](https://adriangm.dev/categoria/inteligencia-artificial/integracion-ia-software/langchain-langgraph-flujo-pasos-decisiones-python)
y
[Pydantic AI: un agente con herramientas y respuestas tipadas en Python](https://adriangm.dev/categoria/inteligencia-artificial/integracion-ia-software/pydantic-ai-agente-herramientas-respuestas-tipadas-python).

Una persona pregunta cuántas plazas quedan en un taller. La aplicación
responde con el nombre del taller y sus plazas o, si la pregunta no permite
identificarlo, con una aclaración. Hay dos formas de obtener la respuesta,
que se eligen con `--engine`:

- `pydantic-ai`, la opción por defecto: un agente de Pydantic AI consulta el
  catálogo con la herramienta `get_available_seats` y devuelve una ficha
  validada.
- `langgraph`: LangChain pide al modelo que identifique el taller y un grafo
  de LangGraph elige entre leer las plazas del catálogo o pedir una
  aclaración.

En los dos casos, la aplicación comprueba la respuesta contra el catálogo
antes de mostrarla.

```text
$ docker run --rm workshop-seats-agent
Taller: Fotografía nocturna
Plazas disponibles: 3
```

## Contenido

- [Qué hace cada parte](#qué-hace-cada-parte).
- [Ejecutar con Docker](#ejecutar-con-docker).
- [Ejecutar sin Docker](#ejecutar-sin-docker).
- [Comprobaciones](#comprobaciones).
- [Estilo y calidad](#estilo-y-calidad).
- [Límites](#límites).

## Qué hace cada parte

El catálogo es ficticio y vive en memoria:

| Taller | Plazas disponibles |
| --- | --- |
| Fotografía nocturna | 3 |
| Cerámica | 0 |

### Con Pydantic AI

Para la pregunta «¿Cuántas plazas quedan para Fotografía nocturna?», el
recorrido es este:

1. El agente envía al modelo la pregunta y la descripción de
   `get_available_seats`: su nombre, su docstring y el argumento
   `workshop_name`, que solo admite «Fotografía nocturna» o «Cerámica».
2. El modelo solicita la herramienta con `workshop_name="Fotografía nocturna"`.
3. Pydantic AI ejecuta la función con el catálogo como dependencia. La
   función devuelve `3`.
4. El modelo propone la ficha final. Pydantic AI la valida con la clase
   `Availability`.
5. El caso de uso compara la ficha con el catálogo y la consola la muestra.

El modelo decide cuándo usar la herramienta y escribe la ficha final, así
que la comparación del paso 5 puede detectar un número mal copiado.

### Con LangChain y LangGraph

La misma pregunta sigue un grafo con tres pasos, `identify`, `answer` y
`clarify`:

1. `identify` envía al modelo unas instrucciones y la pregunta mediante
   LangChain. El modelo devuelve una `WorkshopSelection` con
   `workshop_name="Fotografía nocturna"`, o con `None` si no puede
   identificar el taller.
2. Una función de Python, `choose_next_step`, elige el siguiente paso: hay
   un taller seleccionado, así que va a `answer`.
3. `answer` lee las plazas del catálogo, que LangGraph le entrega como
   contexto de esa ejecución, y construye la respuesta con `3`.
4. El caso de uso compara la respuesta con el catálogo y la consola la
   muestra.

Sin taller seleccionado, el grafo va a `clarify`, que devuelve una
aclaración fija: «Indica el taller: Fotografía nocturna o Cerámica.». Aquí el
modelo solo elige el taller; el recorrido y el número salen de nuestro
código.

### Organización

El código se organiza por responsabilidades:

| Carpeta o módulo | Responsabilidad |
| --- | --- |
| `domain/` | `WorkshopCatalog` guarda las plazas y rechaza datos inválidos. |
| `application/` | `CheckAvailability` pide la respuesta mediante el puerto `AvailabilityAssistant` y rechaza fichas que contradicen el catálogo. |
| `adapters/workshop_name.py` | Nombres de taller que ambos adaptadores aceptan del modelo. |
| `adapters/pydantic_ai/` | Agente, herramienta `get_available_seats`, salida `Availability` y modelo de demostración. |
| `adapters/langgraph/` | Selección `WorkshopSelection`, estado, pasos del grafo, selector de Anthropic y selector de demostración. |
| `bootstrap.py` | Lee la línea de comandos, elige la biblioteca y el modelo y conecta las piezas. |

Los dos adaptadores implementan el mismo puerto. El dominio y la aplicación
no importan Pydantic AI, LangChain ni LangGraph. Las pruebas de arquitectura
lo comprueban.

## Ejecutar con Docker

Requisito: Docker. Construye la imagen desde esta carpeta:

```sh
docker build -t workshop-seats-agent .
```

### Sin cuenta de IA

Sin argumentos, la imagen usa la opción `--demo` y responde la pregunta del
artículo:

```sh
docker run --rm workshop-seats-agent
```

En modo demostración, un `FunctionModel` sustituye al modelo real con reglas
fijas: busca en la pregunta el nombre de un taller del catálogo, solicita la
herramienta y construye la ficha con el número que devuelve. No interpreta el
lenguaje, pero ejecuta el mismo agente, la misma herramienta y las mismas
validaciones. Prueba también estas preguntas:

```sh
docker run --rm workshop-seats-agent --demo "¿Quedan plazas para Cerámica?"
docker run --rm workshop-seats-agent --demo "¿Cuántas plazas quedan?"
```

La primera devuelve cero plazas. La segunda devuelve una aclaración, porque
no nombra ningún taller.

Para usar LangChain y LangGraph, añade `--engine langgraph`:

```sh
docker run --rm workshop-seats-agent --engine langgraph --demo
docker run --rm workshop-seats-agent --engine langgraph --demo "¿Cuántas plazas quedan?"
```

En ese modo, la demostración sustituye solo la selección del modelo: una
regla fija busca el nombre del taller en la pregunta y devuelve una
`WorkshopSelection`. El grafo, su decisión y la lectura del catálogo se
ejecutan igual que con un modelo real.

### Con un modelo de Anthropic

Define la clave y un modelo de tu cuenta compatible con herramientas. Docker
recibe la clave desde tu entorno sin escribirla en el comando:

```sh
export ANTHROPIC_API_KEY=...
export ANTHROPIC_MODEL=...
docker run --rm -e ANTHROPIC_API_KEY -e ANTHROPIC_MODEL \
  workshop-seats-agent "¿Cuántas plazas quedan para Fotografía nocturna?"
```

Con LangGraph, añade `--engine langgraph` antes de la pregunta. En ese caso,
el modelo debe admitir salida estructurada.

En PowerShell, define las variables con `$env:ANTHROPIC_API_KEY = "..."` y
`$env:ANTHROPIC_MODEL = "..."`. Si falta alguna, la aplicación lo indica y
termina con el código 2, sin llamar al proveedor.

Con Pydantic AI, cada pregunta permite como máximo tres peticiones al modelo
y dos ejecuciones de la herramienta. Con LangGraph, cada pregunta hace una
sola petición al modelo. Si el modelo falla, supera esos límites, devuelve
una selección inválida o una ficha que no coincide con el catálogo, la
aplicación muestra el error y termina con el código 1.

## Ejecutar sin Docker

Requisitos: Python 3.15.2 y [uv](https://docs.astral.sh/uv/) 0.13.6.

LangChain depende de PyYAML y zstandard, que aún no publican paquetes
compilados para Python 3.15. uv los compila durante la instalación, así que
hace falta un compilador de C: `gcc` en Linux o las herramientas de línea de
comandos de Xcode en macOS. En Windows sin compilador, usa Docker o WSL.

```sh
uv sync --frozen
uv run workshop-seats --demo
uv run workshop-seats --demo "¿Quedan plazas para Cerámica?"
uv run workshop-seats --engine langgraph --demo
```

Para usar un modelo real, define `ANTHROPIC_API_KEY` y `ANTHROPIC_MODEL` y
ejecuta `uv run workshop-seats` con tu pregunta.

## Comprobaciones

Todas las comprobaciones se ejecutan con un único comando:
`scripts/check_quality.py`. El precommit, la CI y la etapa `quality` del
`Dockerfile` usan esa misma entrada.

Con Docker:

```sh
docker build --target quality .
```

La construcción falla si no se cumple alguna comprobación. Sin Docker, desde
el entorno de uv:

```sh
uv run python scripts/check_quality.py
```

### Instalar el hook de precommit

El hook está versionado en `.githooks/pre-commit`, pero Git no lo activa al
clonar. Instálalo una vez en cada copia, desde la carpeta del proyecto:

```sh
git config core.hooksPath .githooks
```

Antes de cada commit, el hook copia a una carpeta temporal el contenido
preparado con `git add` y construye allí la etapa `quality` con Docker. Si
alguna comprobación falla, muestra el motivo y Git no crea el commit. Los
cambios sin preparar no intervienen. Funciona igual desde la terminal, Git
para Windows o GitHub Desktop; solo necesita Docker en marcha. Para lanzarlo
sin hacer un commit, ejecuta el script. Con Git 2.36 o posterior también
sirve `git hook run pre-commit`:

```sh
sh .githooks/pre-commit
```

El control ejecuta, en este orden:

| Paso | Comprobación |
| --- | --- |
| `scripts.check_structure` | Una clase por módulo y nombres de módulo correctos. |
| `ruff check .` | Estilo, imports, nombres, docstrings, errores comunes y complejidad. |
| `ruff format --check .` | Formato, sin reescribir archivos. |
| `mypy` | Tipado estricto de `src` y `scripts`. |
| `pytest` | Dominio, caso de uso, agente y grafo con modelos guionizados, consola y arquitectura. |

Las pruebas no necesitan red ni clave. Con Pydantic AI sustituyen el modelo
con `FunctionModel` y comprueban la consulta al catálogo, la descripción que
recibe el modelo, la aclaración, el rechazo de plazas negativas, el límite de
llamadas y la ficha que contradice el catálogo. Con LangGraph sustituyen el
selector con un `RunnableLambda` y comprueban los mensajes que recibe el
modelo, los dos caminos del grafo, la lectura del catálogo y el rechazo de
una selección que no es `WorkshopSelection`.

La CI de GitHub, en `.github/workflows/quality.yml`, instala las mismas
versiones con uv y ejecuta `scripts/check_quality.py`. En otro trabajo
construye la etapa `quality`, construye la imagen y ejecuta la demostración.

Las decisiones de arquitectura están en `docs/adr/`.

## Estilo y calidad

### Clean Code - Python Style 1.1

Perfil propio de estilo inspirado en Clean Code y adaptado a Python. Cubre
la presentación y la lectura del código, además de su diseño.

Python sigue PEP 8 y PEP 257, con cuatro espacios y 79 columnas. Ruff 0.17.3
comprueba imports, nombres, docstrings, errores comunes y convenciones, y su
formateador conserva la misma longitud. Los identificadores, comentarios,
docstrings y mensajes técnicos están en inglés; los textos que ve la persona,
en español.

| Regla del perfil | Comprobación |
| --- | --- |
| UTF-8, finales LF, salto final y sin espacios sobrantes | Ruff y `.gitattributes`. |
| Cuatro espacios, 79 columnas y espacios alrededor de operadores | Ruff y su formateador. |
| Comillas dobles y docstrings con triple comilla doble | Ruff Q y formateador. |
| Imports explícitos, absolutos, ordenados y sin elementos sin utilizar | Ruff I y F; pruebas AST para los imports relativos. |
| Parámetros y argumentos multilínea con continuaciones coherentes | Formateador, respetando las comas finales. |
| Complejidad ciclomática 10, cinco argumentos, doce ramas, seis retornos y cincuenta sentencias | Ruff C90 y PLR. |
| Separar validación, preparación, ejecución y resultado cuando cambia la intención | Revisión manual. |
| Métodos públicos antes de los auxiliares privados, con el constructor al principio | Revisión manual. |
| Nombres concretos y cláusulas de guarda cuando simplifican el recorrido | Convenciones de Ruff y revisión manual. |

### Una clase por módulo

Cada clase tiene su propio archivo, incluidas excepciones, protocolos,
modelos Pydantic y clases de prueba. En producción, el módulo lleva el nombre
de la clase en `snake_case`: `WorkshopCatalog` vive en
`domain/workshop_catalog.py`. Los módulos de clase no mezclan funciones
sueltas, y `__init__.py` no declara clases. Las funciones con una
responsabilidad concreta, como `seat_tools.py` o `console_output.py`, viven
en módulos propios.

`scripts/check_structure.py` lo comprueba mediante AST, sin importar la
aplicación:

| Código | Incumplimiento |
| --- | --- |
| PYORG001 | Más de una clase en un archivo, incluidas las anidadas. |
| PYORG002 | Nombre de módulo inadecuado o clase dentro de `__init__.py`. |
| PYORG003 | Clase mezclada con funciones de módulo. |

### Fronteras y efectos al importar

`tests/test_architecture.py` analiza los imports con AST. El dominio solo
usa la biblioteca estándar; la aplicación usa el dominio y la biblioteca
estándar. Los adaptadores no dependen de la entrada de consola. Otra prueba
importa todos los módulos en un intérprete nuevo con la construcción de
agentes, grafos y modelos de LangChain bloqueada: importar un módulo no crea
agentes ni llama al modelo.

Las herramientas acreditan solo las reglas que comprueban. Ruff, mypy y las
pruebas no certifican por sí solos los principios de Clean Code: los
nombres, las responsabilidades, los contratos y el tratamiento de errores
también se revisan manualmente.

## Límites

- El catálogo es ficticio y está en memoria. La aplicación consulta plazas;
  no reserva ni modifica el catálogo.
- `WorkshopName` repite los nombres del catálogo como `Literal` para que el
  modelo reciba los valores admitidos. Una prueba comprueba que ambas listas
  coinciden.
- El modo `--demo` no evalúa a un modelo real. Para medir sus decisiones
  harían falta casos con resultados esperados, incluidas preguntas ambiguas
  y talleres sin plazas.
- La validación de tipos garantiza la forma de la ficha. Que el número
  coincida con el catálogo lo comprueba `CheckAvailability`.
- Con LangGraph, el número sale siempre del catálogo, así que esa
  comprobación no debería fallar. Lo que puede equivocarse es la selección
  del taller, y eso solo se mide con casos de prueba sobre un modelo real.
- El grafo no guarda estado entre preguntas: no hay persistencia ni memoria
  de conversación.
