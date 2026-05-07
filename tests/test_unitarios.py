# SE IMPORTA HERRAMIENTAS DEL SISTEMA Y DEL SISTEMA OPERATIVO
import sys
import os
# TRUCO PARA QUE PYTHON PUEDA ENCONTRAR SERVER.PY
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
from unittest.mock import MagicMock, patch # SE IMPORTA MAGICMOCK Y PATCH
from server import broadcast, validar_nombre, validar_mensaje # SE TRAEN LAS FUNCIONES DE SERVER.PY

# TEST PARA VERIFICAR QUE LA FUNCION BROADCAST SI ENVIA MENSAJES A LOS DEMAS (HAPPY PATH)
def test_broadcast_envia_a_otros_clientes():
    # SE CREAN TRES SOCKETS FALSOS PARA
    remitente = MagicMock()
    receptor_uno = MagicMock()
    receptor_dos = MagicMock()

    # SE CREA UN DICCIONARIO PARA SIMULAR QUE HAY TRES PERSONAS CONECTADAS
    clientes_prueba = {
        remitente: "Ara",
        receptor_uno: "Luis",
        receptor_dos: "Andy"
    }

    # SE DEFINE EL MENSAJE DE PRUEBA A ENVIAR
    mensaje_prueba = b"Hola a todos"

    # SE REEMPLAZA EL DICCIONARIO REAL DEL SERVIDOR POR EL DE PRUEBA
    with patch('server.clientes', clientes_prueba):
        # SE LLAMA A LA FUNCION BROADCAST
        broadcast(remitente, mensaje_prueba)

    # SE VERIFICA QUE EL METODO .SEND() SE HAYA LLAMADO SOLAMENTE UNA VEZ CON EL MENSAJE DE PRUEBA
    receptor_uno.send.assert_called_once_with(mensaje_prueba)
    receptor_dos.send.assert_called_once_with(mensaje_prueba)
    # SE VERIFICA QUE EL METODO .SEND() NO SE HAYA LLAMADO
    remitente.send.assert_not_called()

# TEST PARA VERIFICAR SI SOLO HAY UNA PERSONA Y QUE NO INTENTE ENVIAR SU MENSAJE A NADIE
def test_broadcast_sin_otros_clientes():
    remitente = MagicMock() # SE CREA EL SOCKET

    # SE CREA UN DICCIONARIO PARA SIMULAR QUE SOLO HAY UNA PERSONA CONECTADA
    clientes_prueba = {remitente: "Ara"}

    # SE DEFINE EL MENSAJE DE PRUEBA A ENVIAR
    mensaje_prueba = b"Hola a todos"

    # SE REEMPLAZA EL DICCIONARIO REAL DEL SERVIDOR POR EL DE PRUEBA
    with patch('server.clientes', clientes_prueba):
        # SE LLAMA A LA FUNCION BROADCAST
        broadcast(remitente, mensaje_prueba)

    # SE VERIFICA QUE EL METODO .SEND() NO SE HAYA LLAMADO
    remitente.send.assert_not_called()

# TEST PARA VERIFICAR QUE SE ELIMINA A UN CLIENTE EN CASO DE TENER UN ERROR Y NO INTENTE ENVIAR EL MENSAJE
def test_broadcast_elimina_cliente_con_fallo():
    # SE CREAN DOS SOCKETS FALSOS
    remitente = MagicMock()
    receptor_con_fallo = MagicMock()
    # SE INDICA AL SOCKET FALSO QUE TENGA UN ERROR AL INTENTAR LLAMAR AL METODO .SEND()
    receptor_con_fallo.send.side_effect = Exception("Error de red")

    # SE CREA UN DICCIONARIO PARA SIMULAR QUE HAY DOS PERSONAS CONECTADAS
    clientes_prueba = {
        remitente: "Ara",
        receptor_con_fallo: "Luis"
    }

    # SE DEFINE UN MENSAJE DE PRUEBA
    mensaje_prueba = b"Hola"

    # SE REEMPLAZA EL DICCIONARIO REAL DEL SERVIDOR POR EL DE PRUEBA
    with patch('server.clientes', clientes_prueba):
        broadcast(remitente, mensaje_prueba, )

    receptor_con_fallo.close.assert_called_once() # SE VERIFICA SI EL METODO .CLOSE() SE LLAMO
    assert receptor_con_fallo not in clientes_prueba # SE VERIFICA QUE SE HAYA ELIMINADO EL SOCKET DEL DICCIONARIO

# PRUEBAS UNITARIAS DE VALIDACION (TDD)
def test_nombre_valido():
    assert validar_nombre("Luis") == True

def test_nombre_vacio():
    assert validar_nombre("") == False

def test_nombre_espacios():
    assert validar_nombre("   ") == False

def test_mensaje_valido():
    assert validar_mensaje("Hola a todos") == True

def test_mensaje_vacio():
    assert validar_mensaje("") == False

def test_mensaje_espacios():
    assert validar_mensaje("   ") == False