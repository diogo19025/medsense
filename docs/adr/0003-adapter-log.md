# ADR-0003: Adapter para biblioteca de log

- Status: Aceito
- Data: 2026-07-13

## Contexto

O Laboratório exige (item "Adapter") identificar e implementar um cenário de
uso do padrão Adapter, com a sugestão de utilizar uma biblioteca de log.

A camada de negócio (`control`) precisa registrar eventos (cadastro de
usuário, registro de acesso, falhas de persistência). Escrever chamadas
diretas a `logging` (ou a qualquer outra biblioteca) na camada de negócio a
acoplaria a uma dependência de infraestrutura e dificultaria a troca de
biblioteca ou a supressão de log em testes.

## Decisão

1. Definir a **porta** `Logger` (ABC) em `src/infra/logger.py` com o vocabulário
   de domínio: `info()`, `aviso()`, `erro()`. É o **Target** do padrão.
2. Implementar `LoggingAdapter` em `src/infra/logging_adapter.py` como o
   **Adapter**, que traduz a porta para o **Adaptee** `logging.Logger` da
   biblioteca padrão (`info→info`, `aviso→warning`, `erro→error`).
3. Fornecer `LoggerNulo` (Null Object) como implementação padrão sem efeito,
   usada quando nenhum logger é injetado (evita `if logger is not None` na
   camada de negócio e mantém os testes silenciosos).
4. `UsuarioControl` passa a receber um `Logger` por injeção de dependência e
   registra seus eventos exclusivamente através dessa porta. O `main.py`
   injeta o `LoggingAdapter` concreto.

### Papéis do padrão

| Papel do Adapter | Elemento no projeto              |
|------------------|----------------------------------|
| Target           | `Logger` (ABC)                   |
| Adaptee          | `logging.Logger` (stdlib)        |
| Adapter          | `LoggingAdapter`                 |
| Client           | `UsuarioControl` (camada business) |

## Consequências

- A camada de negócio depende apenas da abstração `Logger`, não de `logging`.
- Trocar de biblioteca (loguru, structlog, envio a um serviço externo) passa a
  ser escrever um novo adapter, sem tocar em `control`.
- Testes injetam um dublê (`LoggerEspiao`) para verificar os eventos logados.
- O diagrama de classes (itens de diagrama) deve exibir `Logger`, `LoggerNulo`
  e `LoggingAdapter`, com a marcação «Adapter».

## Referências

- ADR-0002: persistência de usuários e tratamento de exceções.
- ADR-0004: Template Method para relatórios de acesso (cliente do mesmo logger).
