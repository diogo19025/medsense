# ADR-0005: Repository na camada infra com Abstract Factory

- Status: Aceito
- Data: 2026-07-13

## Contexto

O Laboratório exige (item "Repository/infra") implementar o padrão Repository
para separar a comunicação entre a camada de negócio e a camada de
persistência **para todas as entidades** do projeto, usando Factory Method ou
Abstract Factory para criar as entidades ou selecionar o tipo de repositório.

O ADR-0002 introduziu o contrato `RepositorioUsuario` com duas implementações
(arquivo binário e SQLite), mas ele cobria apenas a entidade `Usuario` e
morava em `src/collection`, misturando o código de infraestrutura (pickle,
sqlite3) com as coleções em RAM da camada de negócio. `RegistroAcesso`
existia apenas em memória, e `main.py` instanciava as classes concretas de
repositório diretamente.

## Decisão

1. Criar o pacote `src/infra/persistencia` e mover para lá as
   **implementações concretas** de persistência (pickle, sqlite3). Os
   **contratos** (interfaces ABC) permanecem na camada de negócio
   (`src/collection`), ao lado das coleções em RAM — Inversão de
   Dependência: o negócio define o contrato e nunca importa código de
   infra; a infra implementa. Manter a interface na camada de negócio (e
   não na infra) segue a Regra de Dependência da Clean Architecture, que
   classifica "interface do Repository na infraestrutura" como violação.
2. Ter um contrato de Repository por entidade, em `src/collection`:
   - `RepositorioUsuario` (já existente);
   - `RepositorioAcesso` (novo, para `RegistroAcesso`).
3. Fornecer três implementações por entidade: memória
   (`Repositorio*Memoria`), arquivo binário (pickle) e SQLite. Os
   repositórios de acesso reutilizam a conversão de exceções do ADR-0002
   (`ArquivoPersistenciaError`, `BancoDadosError`).
4. Aplicar **Abstract Factory** em `FabricaRepositorios`: cada fábrica
   concreta (`FabricaRepositoriosMemoria`, `...Arquivo`, `...SQLite`) produz a
   família completa de repositórios de um mesmo mecanismo — um repositório
   por entidade. A família SQLite compartilha o mesmo arquivo de banco
   (tabelas `usuarios` e `acessos`); a família arquivo usa um `.dat` por
   entidade.
5. Selecionar a fábrica pelo nome do mecanismo com `criar_fabrica(mecanismo)`
   e o mapa `MECANISMOS_DISPONIVEIS`, no mesmo estilo do seletor
   `criar_relatorio` do ADR-0004. `main.py` escolhe a fábrica no início da
   execução ("chaveamento") e injeta os repositórios no `UsuarioControl`.
6. `UsuarioControl` passa a receber também `repositorio_acessos`, carregando
   os acessos para a RAM no início e espelhando cada novo registro — com o
   mesmo desfazer-em-falha do cadastro de usuários (ADR-0002, decisão 5).

### Papéis do padrão

| Papel do Abstract Factory | Elemento no projeto                                      |
|---------------------------|----------------------------------------------------------|
| AbstractFactory           | `FabricaRepositorios`                                    |
| ConcreteFactory           | `FabricaRepositoriosMemoria` / `...Arquivo` / `...SQLite` |
| AbstractProduct           | `RepositorioUsuario`, `RepositorioAcesso`                |
| ConcreteProduct           | `RepositorioUsuarioMemoria`, `RepositorioArquivoBinario`, `RepositorioSQLite`, `RepositorioAcesso*` |
| Client                    | `main.py` / `UsuarioControl` (camada business)           |

## Consequências

- A camada de negócio depende apenas dos contratos de Repository; trocar ou
  adicionar um mecanismo (ex.: JSON, servidor remoto) é escrever uma nova
  família e registrá-la em `MECANISMOS_DISPONIVEIS`, sem tocar em `control`.
- As implementações concretas mudaram de `collection.repositorio_*` para
  `infra.persistencia.repositorio_*` (os contratos permanecem em
  `collection`) — mudança de contrato público registrada por este ADR,
  conforme a regra 3 do `CONTRIBUTING.md`.
- Os registros de acesso passam a sobreviver entre execuções nos mecanismos
  duráveis, e os relatórios do ADR-0004 podem cobrir acessos históricos.
- O diagrama de classes deve exibir `FabricaRepositorios` e suas famílias com
  a marcação «Abstract Factory», além de `RepositorioAcesso`.

## Referências

- ADR-0002: persistência de usuários e tratamento de exceções.
- ADR-0003: Adapter para biblioteca de log (precedente da camada infra).
- ADR-0004: Template Method para relatórios de acesso (estilo do seletor).
