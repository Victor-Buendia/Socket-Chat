import socket
import select
import errno
import sys
import threading
import json
import time
import os

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def limparBuffer(my_username):
    print(f'\n{my_username} > ', end='')
    sys.stdout.flush()


def decode_message(receiver):
    message = ''
    has_message = True

    while has_message:
        try:
            char = receiver.recv(1).decode('utf-8')
            message += char

            if char == '}':
                has_message = False
        except KeyboardInterrupt as e:
            print('\n\nO programa foi finalizado abruptamente.')
            os._exit(1)

    return json.loads(message)

def init():
    my_room = input("Escolha a sala: ")

    # Cria um socket com conexão TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Conecta em um ip e porta dados
    client_socket.connect((IP, PORT))

    # Seta a conexão para não-bloqueante, para que o recv() não bloqueie, só retorne algum erro que trataremos adiante
    client_socket.setblocking(False)

    # Prepara o username do participante e manda ele
    # Aqui precisamos codificar para bytes, depois contar o número de bytes e preparar o header com tamanho fixo, que também codificamos para bytes
    # username = my_username.encode('utf-8')
    # room = my_room.encode('utf-8')
    data = {
        'username': my_username,
        'room': my_room,
    }
    encoded_data = json.dumps(data).encode('utf-8')
    username_header = f"{len(encoded_data):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(username_header + encoded_data)

    print('Para sair, digite o comando /SAIR.')
    threading.Thread(target=limparBuffer(my_username)).start()

    while True:
        readers, _, _ = select.select([sys.stdin, client_socket], [], [])
        for reader in readers:
            if reader is client_socket:
                try:
                    message = decode_message(receiver=client_socket)
                    if message["username"] == 'Sistema':
                        match message["message"]:
                            case '404':
                                print('\n\nA sala escolhida não existe. Tente novamente.')
                                time.sleep(3)
                                clear()
                                init()
                            case '501':
                                print('\n\nO limite da sala escolhida foi atingido. Escolha outra sala.')
                                time.sleep(3)
                                clear()
                                init()
                            case '201':
                                time.sleep(3)
                                clear()
                                init()
                            case '200':
                                time.sleep(1)
                                os._exit(1)
                    sys.stdout.flush()
                    print('\033[A \033[A')
                    print(f'\n{message["username"]} > {message["message"]}')
                    threading.Thread(target=limparBuffer(my_username)).start()

                except IOError as e:
                    # Se não vier dados, tentar novamente. Caso dê errado, sys.exit()
                    if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                        print('Reading error: {}'.format(str(e)))
                        sys.exit()
                    continue

                except Exception as e:
                    # Se for uma exceção diferente, deu ruim, pode sair
                    print('Reading error: '.format(str(e)))
                    sys.exit()
            else:
                # Espera o usuário mandar uma mensagem
                threading.Thread(target=limparBuffer(my_username)).start()
                try:
                    message = input()
                except KeyboardInterrupt as e:
                    print('\n\nO programa foi finalizado abruptamente.')
                    os._exit(1)

                if message.upper() == "/SAIR":
                    print('Saindo da sala...')
                    client_socket.shutdown(socket.SHUT_RDWR)
                    client_socket.close()
                    time.sleep(1)
                    clear()
                    init()

                # Se a mensagem não estiver vazia, mande ela
                if message:
                    # Codifica a mensagem para bytes, prepara o header e converte para bytes, como o username acima, e depois mandar
                    message = message.encode('utf-8')
                    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                    client_socket.send(message_header + message)

try:
    my_username = input("Username: ")
    init()
except KeyboardInterrupt as e:
    print('\n\nO programa foi finalizado abruptamente.')
    os._exit(1)