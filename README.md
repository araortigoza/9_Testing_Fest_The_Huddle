# 🧪 Testing Fest

Chat en tiempo real por consola con sockets TCP (evolución multihilo del chat de proyectos anteriores), desarrollado con **TDD (Test-Driven Development)** y acompañado de una suite de tests unitarios y de integración con `pytest`.

## 📋 Descripción

El proyecto está compuesto por tres partes:

- **`server/server.py`**: servidor de chat que atiende a cada cliente en su propio hilo (`threading`), usando un `Lock` para proteger el acceso concurrente al diccionario de clientes conectados.
- **`cliente/cliente.py`**: cliente de consola que se conecta al servidor, pide un nombre de usuario y permite enviar/recibir mensajes en paralelo (un hilo para recibir, el principal para escribir).
- **`tests/`**: suite de tests con `pytest`, separada en tests unitarios (`test_unitarios.py`) y de integración (`test_integracion.py`).

### Validaciones (desarrolladas con TDD)

El servidor incluye tres funciones de validación, cada una desarrollada siguiendo el ciclo **Red → Green → Refactor** (los comentarios en `server.py` conservan las versiones de la fase "Green" comentadas, como registro del proceso):

- `validar_nombre(nombre)`: rechaza nombres vacíos o compuestos solo por espacios.
- `validar_mensaje(mensaje)`: rechaza mensajes vacíos o compuestos solo por espacios.
- `validar_longitud_mensaje(mensaje)`: rechaza mensajes de más de 200 caracteres.

Si un mensaje no pasa alguna validación, el servidor le responde al cliente con un mensaje de sistema (`"SISTEMA: ..."`) explicando el problema, sin reenviarlo al resto de los usuarios.

### Suite de tests

- **`test_unitarios.py`**: prueba la función `broadcast` de forma aislada, usando `unittest.mock.MagicMock` para simular sockets de clientes (sin abrir conexiones reales) y `patch` para reemplazar el diccionario global `clientes` del servidor. Cubre el caso feliz (el mensaje llega a todos menos al remitente), el caso sin otros clientes conectados, y el caso en que falla el envío a un cliente (se lo elimina de la lista). También incluye los tests de las tres funciones de validación.
- **`test_integracion.py`**: levanta una instancia real del servidor en un hilo de fondo (sobre un puerto de prueba distinto al de producción), conecta varios clientes reales por socket, y verifica el comportamiento end-to-end: que el servidor soporte múltiples clientes simultáneos, que los mensajes lleguen a todos los clientes conectados, y que una desconexión abrupta de un cliente no afecte a los demás.

## ⚙️ Requisitos

- Python 3
- `pytest`

Instalación de dependencias:

```bash
pip install pytest
```

`socket`, `threading`, `sys` y `unittest.mock` ya vienen incluidas en la instalación estándar de Python.

## 🚀 Cómo ejecutar

### Correr el chat

1. Iniciar el servidor:

```bash
python server/server.py
```

2. En una o más terminales adicionales, iniciar uno o varios clientes:

```bash
python cliente/cliente.py
```

Por defecto, el servidor escucha en `127.0.0.1:5000`.

### Correr los tests

Desde la raíz del proyecto:

```bash
pytest
```

O, para ver el detalle de cada test:

```bash
pytest -v
```

Los tests de integración usan puertos distintos entre sí (5100, 5101, 5102) y distintos del puerto de producción (5000), para poder correr todo en paralelo sin choques.

## 🧠 Detalles técnicos

- La función `server()` acepta un `socket_server` opcional como parámetro; en producción crea uno nuevo, pero en los tests de integración se le inyecta un socket ya configurado sobre un puerto de prueba, lo que permite levantar el servidor real dentro del mismo proceso de test sin duplicar lógica.
- `broadcast` primero copia el diccionario de clientes dentro del `Lock` (`list(clientes.items())`) y recién después itera y envía los mensajes fuera del lock, para no bloquear al resto de los hilos mientras se hacen los `send()` de red.
- Los tests de integración usan `time.sleep()` en varios puntos (después de conectar un cliente, después de enviar un mensaje) para darle tiempo al servidor a procesar antes de hacer las aserciones, dado que la comunicación por sockets es asincrónica.
