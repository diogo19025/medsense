# ADR-0002: Persistência de usuários e tratamento de exceções

- Status: Aceito
- Data: 2026-06-17

## Contexto

O Laboratório 2 exige (item 3) permitir o armazenamento de usuários numa
coleção também utilizando arquivo binário ou banco de dados — podendo ser
chaveado com o armazenamento em RAM no início da execução — e implementar
tratamento de exceções (por exemplo, `IOException` ou `SQLException`).

Até então o sistema mantinha os usuários apenas em memória
(`UsuarioCollection`), sem nenhum mecanismo durável nem tratamento de falhas de
I/O ou de banco.

Em Python não existem `IOException`/`SQLException`; os equivalentes são
`OSError`/`IOError` (I/O de arquivo) e `sqlite3.Error` (banco de dados).

## Decisão

1. Introduzir o contrato `RepositorioUsuario` (ABC) com `carregar()` e
   `salvar(usuarios)`, isolando a aplicação do mecanismo durável.
2. Fornecer duas implementações, satisfazendo os "2 mecanismos de persistência"
   do item 1:
   - `RepositorioArquivoBinario` (módulo `pickle`);
   - `RepositorioSQLite` (módulo `sqlite3`).
3. Manter a coleção em RAM (`UsuarioCollection`) como cache de trabalho. Quando
   um repositório é informado, ele é carregado para a RAM no início da execução
   ("chaveamento") e espelhado a cada novo cadastro.
4. Converter as exceções de baixo nível em exceções de domínio dedicadas:
   - `OSError`/`pickle.PickleError`/`EOFError` → `ArquivoPersistenciaError`;
   - `sqlite3.Error` → `BancoDadosError`;
   - ambas herdam de `PersistenciaError`.
5. Em caso de falha na persistência durante um cadastro, desfazer a adição em
   RAM, mantendo RAM e meio durável consistentes.
6. Tratar `PersistenciaError` na camada de fronteira (CLI) e na seleção de
   armazenamento em `main.py`.

## Consequências

- O diagrama de classes (item 1) deve passar a exibir `RepositorioUsuario` e
  suas duas implementações, além da hierarquia `PersistenciaError`.
- O mecanismo de armazenamento é escolhido no início da execução, sem alterar
  as camadas de controle e entidade.
- As falhas de I/O e de banco deixam de vazar exceções de biblioteca para a
  interface, que passa a exibir mensagens de erro de domínio.
- Arquivos gerados em tempo de execução (`*.dat`, `*.db`) são ignorados pelo
  controle de versão.

## Referências

- ADR-0001: validação de campos no cadastro de usuário.
- Política de senhas AWS IAM (item 2):
  https://docs.aws.amazon.com/pt_br/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html
