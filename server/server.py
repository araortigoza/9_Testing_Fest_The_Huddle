import socket
import threading

clientes = {} # SE CREA UN DICCIONARIO EN DONDE SE GUARDARAN LOS SOCKETS Y NOMBRES DE LOS CLIENTES
bloqueo = threading.Lock() # LOCK ASEGURA DE QUE SOLO UN HILO MODIFIQUE EL DICCIONARIO A LA VEZ PARA EVITAR QUE EL SERVIDOR EXPLOTE POR CONDICIONES DE CARRERA
DIRECCION_IP = '127.0.0.1' # SE AIGNA UNA DIRECCION IP
PUERTO = 5000 # SE ASIGNA UN PUERTO

# FUNCION PARA MANEJAR CADA CLIENTE
def manejar_cliente(cliente_socket, cliente_direccion):
    try:
        nombre_raw = cliente_socket.recv(1024) # SE ESPERA RECIBIR DATOS DEL CLIENTE (EN ESTE CASO, SU NOMBRE)

        # SI EL NOMBRE DEL CLIENTE NO EXISTE SIGNIFICA QUE EL CLIENTE SE DESCONECTO
        if not nombre_raw:
            print(f"Cliente {cliente_direccion} se desconecto antes de enviar su nombre.") # MUESTRA EN LA TERMINAL DEL SERVIDOR EL MENSAJE
            cliente_socket.close() # SE CIERRA EL SOCKET DEL CLIENTE
            return

        nombre = nombre_raw.decode('utf-8').strip() # SE DECODIFICA EL NOMBRE RECIBIDO EN BYTES A TEXTO Y QUITA ESPACIOS EN BLANCO

        with bloqueo:
            clientes[cliente_socket] = nombre # SE AGREGA AL DICCIONARIO EL SOCKET Y EL NOMBRE DEL CLIENTE

        print(f"{nombre} se ha conectado desde {cliente_direccion}") # MUESTRA EN LA TERMINAL DEL SERVIDOR EL MENSAJE
        broadcast(cliente_socket, f"{nombre} se ha unido al chat.".encode('utf-8')) # ENVIA EL MENSAJE A TODOS LOS DEMAS CLIENTES MENOS AL QUE ACABA DE CONECTARSE

        with bloqueo:
            usuarios_actuales = ", ".join(clientes.values()) # SE EXTRAE DEL DICCIONARIO DE CLIENTES SOLO LOS VALORES (LOS NOMBRES)
        cliente_socket.send(f"Usuarios conectados: {usuarios_actuales}".encode('utf-8')) # ENVIA A CADA CLIENTE ESA "LISTA" DE NOMBRES CONECTADOS

        # BUCLE PRINCIPAL DEL CLIENTE
        while True:
            mensaje = cliente_socket.recv(1024) # SE ESPERA RECIBIR EL MENSAJE DEL CLIENTE

            # SI EL CLIENTE SE DESCONECTO LIMPIAMENTE
            if not mensaje:
                break

            mensaje_texto = mensaje.decode('utf-8').strip() # SE DECODIFICA EL MENSAJE RECIBIDO EN BYTES A TEXTO

            if not validar_mensaje(mensaje_texto):
                cliente_socket.send("SISTEMA: No se pueden enviar mensajes vacios.".encode('utf-8'))
                continue 

            if not validar_longitud_mensaje(mensaje_texto):
                cliente_socket.send("SISTEMA: El mensaje es demasiado largo.".encode('utf-8'))
                continue

            # SI EL MENSAJE EXISTE
            if mensaje_texto:
                print(f"<{nombre}>: {mensaje_texto}") # SE MUESTRA EN LA TERMINAL DEL SERVIDOR EL NOMBRE JUNTO CON EL MENSAJE
                broadcast(cliente_socket, f"<{nombre}>: {mensaje_texto}".encode('utf-8')) # ENVIA EL MENSAJE RECIBIDO A TODOS LOS DEMAS CLIENTES CONECTADOS

    # IDENTIFICA SI EL CLIENTE SE DESCONECTO ABRUPTAMENTE
    except ConnectionResetError:
        pass

    # IDENTIFICA CUALQUIER OTRO ERROR
    except OSError:
        pass

    finally:
        with bloqueo:
            # SI EL CLIENTE ESTA EN EL DICCIONARIO DE CLIENTES
            if cliente_socket in clientes:
                nombre = clientes[cliente_socket] # SE TRAE EL NOMBRE DEL CLIENTE DEL DICCIONARIO
                del clientes[cliente_socket] # ELIMINA DEL DICCIONARIO DE CLIENTES AL CLIENTE DESCONECTADO
                print(f"{nombre} se desconectó.") # SE MUESTRA EN LA TERMINAL DEL SERVIDOR QUIEN SE DESCONECTO

        broadcast(cliente_socket, f"{nombre} se ha desconectado.".encode('utf-8')) # SE INFORMA A LOS DEMAS CLIENTES QUIEN SE DESCONECTO
        cliente_socket.close() # SE CIERRA EL SOCKET DEL CLIENTE DESCONECTADO

# SE CREA LA FUNCION PRINCIPAL DEL SERVIDOR
def server(socket_server=None): # ASIGNAMOS socket_server COMO NONE PARA PODER INYECTAR UN SOCKET DE PRUEBA PARA LOS TESTS
    if socket_server is None:
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # SE CREA EL OBJETO SOCKET DEL SERVIDOR CON IPv4 Y TCP
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # ESTA FUNCION NOS PERMITE REUTILIZAR LA DIRECCION IP Y EL PUERTO EN CASO DE CERRAR EL SERVIDOR Y QUERER ACTIVARLO RAPIDAMENTE
        socket_server.bind((DIRECCION_IP, PUERTO)) # SE ENLAZA LA DIRECCION IP Y EL PUERTO
        socket_server.listen(5) # SE ACTIVA EL MODO ESCUCHA DEL SERVIDOR
        print(f"Escuchando en: {DIRECCION_IP}: Puerto:{PUERTO}") # SE IMPRIME MENSAJE

    # BUCLE PRINCIPAL
    while True:
        try:
            cliente_socket, cliente_direccion = socket_server.accept() # SE ACEPTA LA CONEXION Y SE CREA UN NUEVO SOCKET PARA EL CLIENTE NUEVO
            print(f"Se acepto conexion de {cliente_direccion}") # MENSAJE
            hilo = threading.Thread(target=manejar_cliente, args=(cliente_socket, cliente_direccion), daemon=True) # SE CREA UN HILO PARA EL CLIENTE
            hilo.start() # SE INICIA EL HILO
        except OSError:
            break

# SE CREA LA FUNCION DE BROADCAST
def broadcast(sender_socket, mensaje):
    with bloqueo:
        lista = list(clientes.items()) # SE CREA UNA COPIA DEL DICCIONARIO PARA ITERAR

    # SE RECORRE LA COPIA DEL DICCIONARIO
    for client_socket, _ in lista:
        # SI EL CLIENTE ES DIFERENTE DEL CLIENTE QUE ENVIO EL MENSAJE
        if client_socket != sender_socket:
            try:
                client_socket.send(mensaje) # SE ENVIA EL MENSAJE A LOS DEMAS CLIENTES

            # IDENTIFICA SI ALGO FALLO CON EL CLIENTE AL MOMENTO DE ENVIAR EL MENSAJE
            except:
                client_socket.close() # SE CIERRA EL SOCKET DEL CLIENTE
                with bloqueo:
                    # SI EL CLIENTE ESTA EN EL DICCIONARIO DE CLIENTES
                    if client_socket in clientes:
                        del clientes[client_socket] # SE LO ELIMINA

# ... TDD (TEST-DRIVEN DEVELOPMENT) ...

# FUNCION PARA VALIDAR QUE UN NOMBRE DE USUARIO NO ESTE VACIO
# --- FASE GREEN ---
# def validar_nombre(nombre):
#     if nombre == " ": 
#         return False
#     return True

# --- FASE REFACTOR ---
def validar_nombre(nombre):
    if not nombre or not nombre.strip():
        return False
    return True

# --- FASE GREEN ---
# def validar_mensaje(mensaje):
#     if mensaje == " ":
#         return False
#     return True

# --- FASE REFACTOR ---
def validar_mensaje(mensaje):
    if not mensaje or not mensaje.strip():
        return False
    return True

# --- FASE GREEN ---
# def validar_longitud_mensaje(mensaje):
#     # SE VERIFICA SI EL MENSAJE EXISTE
#     if mensaje == None:
#         return False
    
#     # SE CUENTAN LOS CARACTERES DEL MENSAJE
#     cuenta = len(mensaje)
    
#     # SE COMPARAN LOS VALORES
#     if cuenta <= 200:
#         return True
#     else:
#         return False

# --- FASE REFACTOR ---
def validar_longitud_mensaje(mensaje):
    if not mensaje:
        return False
    return len(mensaje) <= 200

if __name__ == "__main__":
    server()