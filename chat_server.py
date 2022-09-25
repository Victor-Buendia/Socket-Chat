import socket
import select
import os
import time
import json
import threading

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

comandos = {
    "/CRIAR": "Cria uma nova sala.",
    "/LISTAR": "Listar salas criadas.",
    "/ENCERRAR": "Encerrar uma sala.",
    "/SAIR": "Encerrar a aplicação.",
    "/LOGS": "Exibir logs"
}

logs = []

# Cria um socket com conexão TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, para que o servidor informe ao sistema operacional que ele usará determinado IP e porta
server_socket.bind((IP, PORT))

# Servidor está ouvindo novas conexões
server_socket.listen()

# Lista de sockets para o select()
sockets_list = [server_socket]

# Lista de clientes conectados (socket como chave, header do usuário e nome)
clients = {}

# Lista de salas abertas contendo limite de usuários e usuários conectados
rooms = []


def add_user_to_room(room_name, user):
    room_selected = None
    for room in rooms:
        if room['name'] == room_name:
            room_selected = room

    if room_selected is not None:
        room_limit = room_selected['limit']
        if (len(room_selected['users']) + 1) <= room_limit:
            room_selected['users'].append(user)
            user['room'] = room_selected
            clients[user['socket']] = user

            notify_user_join_room(username_join=user['username'], room=room_selected)
            log_message(f'{user["username"]} entrou na sala {room_selected["name"]}.')

            return room_selected
        else:
            log_message(f'{user["username"]} tentou entrar na sala \'{room_selected["name"]}\', mas seu limite de participantes já foi atingido.')
            data = {'username': 'Sistema', 'message': '501'}
            encoded_data = json.dumps(data).encode('utf-8')
            user['socket'].send(encoded_data)

            user['socket'].shutdown(socket.SHUT_RDWR)
            user['socket'].close()
            # raise Exception('Limite da sala atingido.')
    else:
        log_message(f'{user["username"]} tentou entrar em sala inexistente.')
        data = {'username': 'Sistema', 'message': '404'}
        encoded_data = json.dumps(data).encode('utf-8')
        user['socket'].send(encoded_data)

        user['socket'].shutdown(socket.SHUT_RDWR)
        user['socket'].close()
        # raise Exception('Sala não encontrada.')


def check_sockets_list():
    for checking_socket in sockets_list:
        if checking_socket.fileno() == -1:
            sockets_list.remove(checking_socket)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def create_room():
    print('\nCriando sala...')

    try:
        room_name = input('Digite o nome da sala: ')
        room_limit = input('Digite o limite da sala: ')
        room_id = (rooms[len(rooms) - 1]['id'] + 1) if (len(rooms) > 0) else 1
        rooms.append({'id': room_id, 'name': room_name, 'limit': int(room_limit), 'users': []})
    except ValueError as e:
        print('\nInsira dados válidos.')
        time.sleep(3)
        clear()
        create_room()

    clear()
    print(f'Sala {room_name} criada.')
    log_message(f'Sala {room_name} criada. Atualmente, existem {len(rooms)} salas criadas.')


def delete_room():
    show_rooms()
    room_to_be_removed = None

    id_room_to_be_removed = input('Selecione o id da sala a ser removida:')
    for room in rooms:
        if room['id'] == int(id_room_to_be_removed):
            room_to_be_removed = room
            continue

    if room_to_be_removed is not None:
        remove_users_from_room(room=room_to_be_removed)
        rooms.remove(room_to_be_removed)
        print("Sala encerrada")
        log_message(f'Sala {room_to_be_removed["name"]} foi encerrada.')
        threading.Thread(target=manage_sockets).start()

    else:
        print('Sala não encontrada.')

def init():
    threading.Thread(target=manage_sockets).start()
    log_message(f'Esperando conexões em {IP}:{PORT}...')
    option = ''
    first_time = 0
    while True:
        print(option)
        match option.upper():
            case '/CRIAR':
                create_room()

            case '/LISTAR':
                show_rooms()
                input('Pressione uma tecla para continuar...')
                print('\n\n')

            case '/LOGS':
                show_logs()

            case '/ENCERRAR':
                delete_room()

            case '/SAIR':
                print('\nEncerrando aplicação...')
                os._exit(1)

            case _:
                if first_time != 0:
                    print('\nComando Inválido!')
                    time.sleep(1)
                first_time = 1
        clear()
        option = menu()


def menu():
    print('================== MENU ==================')
    for comando in comandos:
        print(f'{comando} -----> {comandos[comando]}')
    try:
        option = input('Digite um comando: ')
    except KeyboardInterrupt as e:
        print('\n\nO programa foi finalizado abruptamente.')
        os._exit(1)

    return option


def log_message(message):
    logs.append(message)


# Lidando com o recebimento de mensagem
def receive_message(client_socket):
    try:

        # Recebe o "header" contendo o tamanho da mensagem
        message_header = client_socket.recv(HEADER_LENGTH)

        # Se não recebermos dados, o servidor irá encerrar a conexão, usando socket.close() ou socket.shutdown(socket.SHUT_RDWR)
        if not len(message_header):
            return False

        # Converte o header para inteiro
        message_length = int(message_header.decode('utf-8').strip())

        # Retorna o header da mensagem e os dados
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:

        # Se chegar aqui, o cliente encerrou a conexão abruptamente (ctrl+c)
        # ou só perdeu a conexão
        return False


def manage_sockets():
    while True:
        check_sockets_list()
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

        # Iterar nos sockets notificados
        for notified_socket in read_sockets:

            # Se o socket notificado é um socket servidor, aceitar a conexão
            if notified_socket == server_socket:

                # Aceita nova conexão
                # Isso nos dá um novo soquete - soquete do cliente, conectado apenas a esse determinado cliente (exclusivo)
                # O outro objeto retornado é ip/port set
                client_socket, client_address = server_socket.accept()

                # Mandando o nome do cliente
                user = receive_message(client_socket)
                # Se for falso, o cliente caiu antes de mandar o nome
                if user is False:
                    continue

                # Adicionar socket aceito à lista do select
                sockets_list.append(client_socket)

                # Salvar o username e o header
                data = json.loads(user['data'].decode('utf-8'))
                username = data['username']
                room = data['room']

                add_user_to_room(room_name=room, user={'socket': client_socket, 'username': username})

            # Else, socket já existente está enviando uma mensagem
            else:
                send_message(socket=notified_socket)
        for notified_socket in exception_sockets:
            try:
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
            except Exception as e:
                log_message(f'Erro ao remover socket que deu errado: {e}')


def notify_user_left_room(username_left, room):
    for user in room['users']:
        data = {'username': username_left, 'message': '*** SAIU DA SALA ***'}
        encoded_data = json.dumps(data).encode('utf-8')
        try:
            user['socket'].send(encoded_data)
        except Exception as e:
            log_message(f'Não foi possível enviar mensagem: {e}')


def notify_user_join_room(username_join, room):
    for user in room['users']:
        data = {'username': username_join, 'message': '*** ENTROU NA SALA ***'}
        encoded_data = json.dumps(data).encode('utf-8')
        user['socket'].send(encoded_data)


def remove_users_from_room(room):
    for user in room['users']:
        data = {'username': 'Sistema', 'message': '*** ESTA SALA FOI ENCERRADA ***'}
        encoded_data = json.dumps(data).encode('utf-8')
        user['socket'].send(encoded_data)

        user['socket'].shutdown(socket.SHUT_RDWR)
        user['socket'].close()


def remove_socket(socket_closed):
    user_left = clients[socket_closed]
    room_user_left = user_left['room']
    room_user_left['users'].remove(user_left)

    notify_user_left_room(username_left=user_left['username'], room=room_user_left)

    del clients[socket_closed]
    sockets_list.remove(socket_closed)
    log_message(f'Conexão encerrada de: {user_left["username"]}')


def send_message(socket):
    # Recebe mensagem
    message = receive_message(socket)

    # Se for falso, cliente desconectou, pode limpar
    if message is False:
        remove_socket(socket)
        return

    # Pegar o usuário do socket notificado, para saber quem enviou a mensagem
    sender_user = clients[socket]
    username = sender_user['username']

    log_message(f'{username} [{sender_user["room"]["name"]}]: {message["data"].decode("utf-8")}')

    # Iterar sobre os clientes conectados e a mensagem broadcast
    for user in sender_user['room']['users']:

        # Não enviar para quem enviou
        if user['socket'] != socket:
            data = {'username': username, 'message': message['data'].decode('utf-8')}
            encoded_data = json.dumps(data).encode('utf-8')

            # Enviar usuário e mensagem com seus headers
            # Reutilizando header da mensagem enviada pelo transmissor e salvando username enviado pelo usuário na conexão
            user['socket'].send(encoded_data)


def show_logs():
    clear()
    print('****** LOGS ******')

    for log in logs:
        print(f'- {log}')

    input('Pressione uma tecla para continuar...')
    print('\n\n')


def show_rooms():
    clear()
    print('****** SALAS ******')
    for room in rooms:
        print(f'{room["id"]}: {room["name"]} - {len(room["users"])}/{room["limit"]} usuários conectados.')

# Iniciar o programa
try:
    init()
except KeyboardInterrupt as e:
    print('\n\nO programa foi finalizado abruptamente.')
    os._exit(1)