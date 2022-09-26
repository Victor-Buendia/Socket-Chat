# Fundamento de Redes de Computadores

## Trabalho Final

Este repositório foi criado para o desenvolvimento de ambientes virtuais de conversação com uso system call select() como conclusão da disciplina de FRC.

- O roteiro utilizado pode ser encontrado clicando aqui [Roteiro](/Roteiro.pdf).

- O relatório pode ser encontrado clicando aqui [Relatório](/Relat%C3%B3rio.pdf)

- A apresentação em slides pode ser encontrada clicando aqui [Apresentação](Apresentação.pdf)

## Alunos

| Aluno                        | Matrícula |
| ---------------------------- | --------- |
| João Vitor de Souza Durso    | 180123459 |
| Victor Buendia Cruz de Alvim | 190020601 |
| Yan Andrade Sena             | 180123459 |

## Como executar o trabalho

Para executar o trabalho, deve ser realizada a instalação do Python 3.10 ou superior.

Com  o python instalado, executar o seguinte comando para rodar o servidor: 
```
python3.10 chat_server.py
```

Com servidor rodando, executar o comando abaixo para rodar o cliente:
```
python3.10 chat_client.py
```

A partir disso, basta seguir às instruções da aplicação no próprio terminal.

### Inspiração

Os arquivos client.py e server.py são arquivos utilizados para estudo durante o desenvolvimento do trabalho. Eles foram usados para implementar a lógica em um programa mais simples para depois escalar para o projeto maior. Para rodá-los:

Terminal Servidor
```python
nc -l 1234
```

Terminal Cliente
```python
python3.10 client.py
```