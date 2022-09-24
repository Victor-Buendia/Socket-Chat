import socket
import select
import errno
import sys
import threading

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
my_username = input("Username: ")

def limparBuffer(my_username):
    print(f'\n{my_username} > ', end = '')
    sys.stdout.flush()

# Cria um socket com conexão TCP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Conecta em um ip e porta dados
client_socket.connect((IP, PORT))

# Seta a conexão para não-blocante, para que o recv() não bloqueie, só retorne algum erro que trataremos adiante
client_socket.setblocking(False)

# Prepara o username do participante e manda ele
# Aqui precisamos codificar para bytes, depois contar o número de bytes e preparar o header com tamanho fixo, que também codificamos para bytes
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

threading.Thread(target=limparBuffer(my_username)).start()

while True:
    readers,_,_ = select.select([sys.stdin, client_socket], [], [])
    for reader in readers:
        if reader is client_socket:
            try:
                # Agora fazemos um loop nas mensagens recebidas e as printamos
                while True:

                    # Recebe o header contendo o tamanho do username
                    username_header = client_socket.recv(HEADER_LENGTH)

                    # Se não recebermos dados, o servidor irá encerrar a conexão, usando socket.close() ou socket.shutdown(socket.SHUT_RDWR)
                    if not len(username_header):
                        print('Conexão encerrada pelo servidor.')
                        sys.exit()

                    # Converte o header para inteiro
                    username_length = int(username_header.decode('utf-8').strip())

                    # Recebe e decodifica o username
                    username = client_socket.recv(username_length).decode('utf-8')

                    # Agora fazemos o mesmo para a mensagem (como recebemos o nome de usuário, recebemos a mensagem inteira, não há necessidade de verificar se ela tem algum comprimento)
                    message_header = client_socket.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = client_socket.recv(message_length).decode('utf-8')

                    # Printa mensagem
                    print(f'{username} > {message}')
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
            message = input()

            # Se a mensagem não estiver vazia, mande ela
            if message:
                # Codifica a mensagem para bytes, prepara o header e converte para bytes, como o username acima, e depois mandar
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                client_socket.send(message_header + message)

