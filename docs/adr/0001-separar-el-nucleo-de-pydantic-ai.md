# 0001. Separar el núcleo de Pydantic AI

## Estado

Aceptada.

## Contexto

El taller enseña a usar Pydantic AI: el agente, la herramienta
`get_available_seats`, las dependencias con `RunContext` y la salida
validada `Availability`. Esas piezas cambian con la biblioteca y con el
proveedor del modelo. El catálogo y la decisión de aceptar una respuesta, en
cambio, pertenecen a la aplicación.

Una ficha validada puede tener la forma correcta y un dato equivocado: treinta
plazas cuando el catálogo tiene tres.

## Decisión

- `domain/WorkshopCatalog` guarda las plazas, rechaza nombres vacíos y
  cantidades negativas, y distingue un taller desconocido de uno sin plazas.
- `application/CheckAvailability` usa el puerto `AvailabilityAssistant`.
  Acepta una aclaración tal cual, pero compara cada ficha con el catálogo y
  rechaza la que no coincide con `InconsistentReportError`.
- `adapters/pydantic_ai/` implementa el puerto con Pydantic AI y traduce
  `Availability` o el texto de aclaración a los tipos de la aplicación.
- `bootstrap.py` conecta las piezas y es el único módulo que conoce la línea
  de comandos y las variables de entorno.

Las pruebas AST impiden que el dominio o la aplicación importen Pydantic AI.

## Consecuencias

- El caso de uso se prueba con un doble sencillo, sin modelo ni red.
- Cambiar de biblioteca o de proveedor afecta al adaptador y a la composición.
- La aplicación repite la consulta al catálogo para verificar la ficha.
  Con un catálogo en memoria ese coste es despreciable. Con un servicio
  remoto habría que revisar si la segunda lectura sigue siendo adecuada.
- `WorkshopName` repite los nombres del catálogo como `Literal` para que el
  modelo reciba los valores admitidos. Una prueba comprueba que coinciden.
