# Fundamento de Redes de Computadores

## Trabalho Final

Este repositório foi criado para o desenvolvimento de ambientes virtuais de conversação com uso system call select() como conclusão da disciplina de FRC.

O roteiro utilizado pode ser encontrado clicando aqui [Roteiro](/FRC_PROJ_PESQUISA_SALAS_BATE_PAPO.pdf).

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

### Inspiração

Os arquivos client.py e server.py são arquivos utilizados para estudo durante o desenvolvimento do trabalho. Para rodá-los:

Terminal Servidor
```python
nc -l 1234
```

Terminal Cliente
```python
python3 client.py
```