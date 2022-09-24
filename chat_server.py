import socket
import select

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234

# Cria um socket com conexão TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, para que o servidor informe ao sistema operacional que ele usará determinado IP e porta
server_socket.bind((IP, PORT))

# Servidor está ouvindo novas conexões
server_socket.listen()

# Lista de sockets para o select()
sockets_list = [server_socket]

# Lista de clientes conectados (socket como chave, header do usuário e nome
clients = {}

print(f'Esperando conexões em {IP}:{PORT}...')
print('Para criar uma nova sala tecle 1')
print('Para listar os participantes de uma sala tecle 2')


# Ver como executar esse comando em loop
comandos = input()
if comandos == '1':
    print("insira aqui um número para uma sala")
    num = input()
    PORT = num
    print(f'Mudando para sala {IP}:{PORT}...')
if comandos == '2':
    print(clients)
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

while True:
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
            clients[client_socket] = user

            print('{} entrou na sala.'.format(user['data'].decode('utf-8')))

        # Else, socket já existente está enviando uma mensagem
        else:

            # Recebe mensagem
            message = receive_message(notified_socket)

            # Se for falso, cliente disconectou, pode limpar
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Remove da lista do socket
                sockets_list.remove(notified_socket)

                # Remove da lista de usuários
                del clients[notified_socket]

                continue

            # Pegar o usuário do socket notificado, para saber quem enviou a mensagem
            user = clients[notified_socket]

            print(f'{user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Iterar sobre os clientes conectados e a mensagem broadcast
            for client_socket in clients:

                # Não enviar para quem enviou
                if client_socket != notified_socket:

                    # Enviar usuário e mensagem com seus headers
                    # Reutilizando header da mensagem enviada pelo transmissor e salvando username enviado pelo usuário na conexão
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:

        sockets_list.remove(notified_socket)

        del clients[notified_socket]