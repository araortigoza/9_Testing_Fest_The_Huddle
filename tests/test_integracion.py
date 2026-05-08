# SE IMPORTA HERRAMIENTAS DEL SISTEMA Y DEL SISTEMA OPERATIVO
import sys
import os
# TRUCO PARA QUE PYTHON PUEDA ENCONTRAR SERVER.PY
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))
import socket
import threading
import time
import server

# SE DEFINE UNA DIRECCION IP
DIRECCION_IP = '127.0.0.1'

# FUINCION PARA CREAR EL SERVIDOR DE PRUEBA
def crear_servidor_prueba(puerto):
    server.clientes.clear() # SE LIMPIA EL DICCIONARIO DE CLIENTES DENTRO DE SERVER.PY

    # SE CONFIGURA TOD EL SERVIDOR Y SE PONE EN ESCUCHA
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_server.bind((DIRECCION_IP, puerto))
    socket_server.listen(5)

    # SE CREA EL HILO PARA EL SERVIDOR DE PRUEBA
    hilo = threading.Thread(target=server.server, args=(socket_server,), daemon=True)
    hilo.start()
    time.sleep(0.1) # SE ESPERA ESE TIEMPO PARA ASEGURAR QUE EL HILO ARRANCO ANTES CONECTAR CLIENTES
    return socket_server

# FUNCION PARA CONECTAR CLIENTES AL SERVIDOR DE PRUEBA
def conectar_cliente(nombre, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((DIRECCION_IP, puerto))
    cliente.send(nombre.encode('utf-8'))
    time.sleep(0.5)
    return cliente

# TEST PARA ASEGURAR QUE EL SERVIDOR PUEDA MANEJAR MAS DE UN HILO DE CLIENTE
def test_multiples_clientes_se_conectan():
    puerto = 5100 # SE DEFINE EL PUERTO
    socket_server = crear_servidor_prueba(puerto) # SE CREA EL SERVIDOR

    # SE INICIALIZA A DOS CLIENTES COMO NONE
    cliente_uno = None
    cliente_dos = None

    try:
        # SE INTENTA CONECTAR A AMBOS CLIENTES
        cliente_uno = conectar_cliente("Ara", puerto)
        cliente_dos = conectar_cliente("Luis", puerto)

        # SE VERIFICA QUE EN EL DICCIONARIO DE CLIENTES HAYAN DOS CONEXIONES
        assert len(server.clientes) == 2

    # FINALMENTE SE CIERRAN TODAS LAS CONEXIONES
    finally:
        if cliente_uno:
            cliente_uno.close()
        if cliente_dos:
            cliente_dos.close()
        socket_server.close()

# TEST PARA VERIFICAR QUE LOS CLIENTES REALMENTE SE COMINUCAN ENTRE SI
def test_mensaje_llega_a_todos_los_clientes():
    puerto = 5101 # SE DEFINE EL PUERTO
    socket_server = crear_servidor_prueba(puerto) # SE CREA EL SERVIDOR DE PRUEBA

    # SE ASIGNAN A TRES CLIENTES CON NONE
    cliente_uno = None
    cliente_dos = None
    cliente_tres = None

    try:
        # SE INTENTA COENCTAR A LOS TRES CLIENTES
        cliente_uno = conectar_cliente("Ara", puerto)
        cliente_dos = conectar_cliente("Luis", puerto)
        cliente_tres = conectar_cliente("Andy", puerto)

        # SE INDICA QUE UN SOCKET ESPERE SOLO POR 2 SEGUNDOS RECIBIR UN MENSAJE, SONO LANZA UN ERROR
        cliente_uno.settimeout(2)
        cliente_dos.settimeout(2)
        cliente_tres.settimeout(2)

        # SE HACE QUE ARA LEA EL PRIMER MENSAJE ENVIADO POR EL SERVIDOR PARA QUE LA BANDEJA QUEDE VACIA
        cliente_uno.recv(1024)

        mensaje_prueba = "Hola a todos" # SE DEFINE UN MENSAJE DE PRUEBA
        cliente_uno.send(mensaje_prueba.encode('utf-8')) # ARA ENVIA ESE MENSAJE DE PRUEBA CODIFICANDOLO EN BYTES
        time.sleep(0.3) # SE PAUSA POR ESE TIEMPO PARA QUE EL SERVIDOR HAGA LO SUYO

        # LUIS Y ANDY RECIBEN EL MENSAJE EN TEXTO
        respuesta_dos = cliente_dos.recv(1024).decode('utf-8')
        respuesta_tres = cliente_tres.recv(1024).decode('utf-8')

        # SE VERIFICA QUE LUIS Y ANDY HAYAN RECIBIDO EL MISMO MENSAJE EN EL FORMATO ESPERADO
        assert "<Ara>: Hola a todos" in respuesta_dos
        assert "<Ara>: Hola a todos" in respuesta_tres

    # FINALMENTE SE CIERRAN TODAS LAS CONEXIONES
    finally:
        if cliente_uno:
            cliente_uno.close()
        if cliente_dos:
            cliente_dos.close()
        if cliente_tres:
            cliente_tres.close()
        socket_server.close()


def test_desconexion_abrupta_no_afecta_otros_clientes():
    puerto = 5102 # SE DEFINE EL PUERTO
    socket_server = crear_servidor_prueba(puerto) # SE CREA EL SERVIDOR DE PRUEBA

    # SE ASIGNAN A TRES CLIENTES CON NONE
    cliente_uno = None
    cliente_dos = None
    cliente_tres = None

    try:
        # SE INTENTA COENCTAR A LOS TRES CLIENTES
        cliente_uno = conectar_cliente("Ara", puerto)
        cliente_dos = conectar_cliente("Luis", puerto)
        cliente_tres = conectar_cliente("Andy", puerto)

        # SE INDICA QUE UN SOCKET ESPERE SOLO POR 2 SEGUNDOS RECIBIR UN MENSAJE, SONO LANZA UN ERROR
        cliente_uno.settimeout(2)
        cliente_dos.settimeout(2)
        cliente_tres.settimeout(2)

        # SE HACE QUE ARA LEA EL PRIMER MENSAJE ENVIADO POR EL SERVIDOR PARA QUE LA BANDEJA QUEDE VACIA
        cliente_uno.recv(1024)

        cliente_dos.close() # SE SABOTEA LA CONEXION DE LUIS
        cliente_dos = None # SE ASIGNA COMO NONE PARA QUE FINALLY NO INTENTE VOLVER A CERRARLA
        time.sleep(0.5) # SE LE DA EL TIEMPO AL SERVIDOR PARA QUE HAGA LO SUYO

        assert len(server.clientes) == 2 # SE VERIFICA QUE SOLO QUEDEN DOS PERSONAS
        assert "Ara" in server.clientes.values() # SE VERIFICA QUE ARA SIGA
        assert "Andy" in server.clientes.values() # SE VERIFICA QUE ANDY SIGA
        assert "Luis" not in server.clientes.values() # SE VERIFICA QUE LUIS NO ESTE

        cliente_uno.send(b"Sigo conectado") # ARA ENVIA UN MENSAJE PARA VER SI EL SERVIDOR SIGUE FUNCIONANDO
        time.sleep(0.3) # SE LE DA TIEMPO AL SERVIDOR PARA QUE HAGA LO SUYO

        respuesta_tres = cliente_tres.recv(1024).decode('utf-8') # ANDY RECIBE EL MENSAJE DE ARA
        assert "<Ara>: Sigo conectado" in respuesta_tres # SE VERIFICA QUE ANDY HAYA RECIBIDO EL MENSAJE EN EL FORMATO ESPERADO

    # SE CIERRAN TODAS LAS CONEXIONES
    finally:
        if cliente_uno:
            cliente_uno.close()
        if cliente_dos:
            cliente_dos.close()
        if cliente_tres:
            cliente_tres.close()
        socket_server.close()