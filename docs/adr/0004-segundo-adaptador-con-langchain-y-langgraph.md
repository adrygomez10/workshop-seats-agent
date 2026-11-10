# 0004. Segundo adaptador con LangChain y LangGraph

## Estado

Aceptada.

## Contexto

El artículo de LangChain y LangGraph resuelve la misma pregunta que el de
Pydantic AI: cuántas plazas quedan en un taller, con una aclaración cuando no
se puede identificar. Su planteamiento es distinto. En Pydantic AI, el modelo
decide cuándo usar la herramienta y escribe la ficha final. En LangGraph, el
modelo solo selecciona el taller y el código decide el recorrido y construye
la respuesta con el catálogo.

La aplicación ya recibe el asistente mediante el puerto
`AvailabilityAssistant`, sin depender de la biblioteca que hay detrás.

## Decisión

- `adapters/langgraph/` implementa el mismo puerto con un grafo de tres
  pasos: `identify`, `answer` y `clarify`. LangChain obtiene una
  `WorkshopSelection` del modelo con salida estructurada.
- El catálogo llega a los pasos como contexto de cada ejecución, envuelto en
  `WorkflowContext`, porque LangGraph solo admite dataclasses, `TypedDict` o
  modelos de Pydantic como contexto. El dominio no cambia.
- La opción `--engine` de la consola elige entre `pydantic-ai`, la opción por
  defecto, y `langgraph`. Las dos usan el mismo catálogo, el mismo caso de
  uso y la misma salida.
- `WorkshopName` pasa a `adapters/workshop_name.py`, compartido por los dos
  adaptadores.
- El modo `--demo` de LangGraph sustituye solo el selector por una regla fija
  con `RunnableLambda`.
- Los errores propios de cada adaptador se capturan en `bootstrap.py`, la
  única pieza que conoce los dos. El adaptador de LangGraph los reúne en
  `WORKFLOW_ERRORS`.

## Consecuencias

- Las mismas pruebas de arquitectura vigilan los dos adaptadores, y la
  importación de módulos no construye grafos ni modelos.
- LangChain depende de PyYAML y zstandard, sin paquetes compilados para
  Python 3.15. El `Dockerfile` instala `gcc` en una etapa de construcción y
  la imagen final copia solo el entorno virtual. Sin Docker, la instalación
  necesita un compilador de C.
- Con LangGraph, la comparación de `CheckAvailability` no debería fallar,
  porque el número sale del catálogo. Se mantiene porque es una regla del
  caso de uso, no de un adaptador.
- La imagen pasa a incluir dos bibliotecas de IA aunque cada ejecución use
  una sola.
