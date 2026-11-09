# 0002. Modelo guionizado para ejecutar sin cuenta

## Estado

Aceptada.

## Contexto

Quien sigue el taller debe poder ejecutar el recorrido completo aunque no
tenga una clave de Anthropic. Las pruebas tampoco deben depender de la red ni
de las respuestas variables de un modelo real.

Pydantic AI ofrece `TestModel`, que genera llamadas y salidas a partir de los
esquemas, y `FunctionModel`, que delega cada respuesta en una función propia.

## Decisión

La opción `--demo` usa un `FunctionModel` con reglas fijas, definido en
`adapters/pydantic_ai/demo_responses.py`. Busca en la pregunta un nombre de
taller del esquema de la herramienta, solicita `get_available_seats` y
construye la ficha final con el número que devolvió la herramienta. Si no
encuentra ningún taller, responde con una aclaración.

Las pruebas usan esa misma función y otras respuestas guionizadas para los
fallos: plazas negativas y un modelo que no deja de pedir herramientas.

## Consecuencias

- El modo demostración ejecuta el agente, la herramienta, las dependencias,
  la validación de salida y los límites de uso reales de Pydantic AI.
- Las respuestas son deterministas y se pueden comprobar en las pruebas.
- Las reglas no interpretan lenguaje natural. El README y la documentación
  del módulo lo indican para que la demostración no se confunda con una
  evaluación del modelo.
- El modo con modelo real necesita `ANTHROPIC_API_KEY` y `ANTHROPIC_MODEL`.
  La aplicación lo comprueba antes de crear el agente.
