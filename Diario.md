## Diario de actualizaciones a 2.0

### Migraciones a la ultimas versiones

1. Lo primero que hice fue cambiar la version de python a python 3.11.4
2. Lo segundo fue actualizar las dependencias sus ultimas versiones, python-telegram-bot a la version 20.4, aqui si hubieron muchos cambios que tuve que hacerle al codigo,

- Ahora si se puso await y async en todas las funciones
- await en todas las llamadas a las funciones de python telegram bot
- Cambio la forma de llamar y construir la aplicación

3. Actualización a pytube 15.0.o

- Habia un Bug en el código, de la página cypher.py en la linea 30 se cambio a `var_regex = re.compile(r"^\$\w+\W")` y problema resuelto

4. Actualización de Spotdl

- Habia un problema de Asyncio que decia que ya habia un eventloop corriendo, lo que hice fue instalar el modulo ` nest_asyncio` e inicilizarlo en el código con `nest_asyncio.apply()` y funcionó.

### Arreglos de problemas de la version anterior
