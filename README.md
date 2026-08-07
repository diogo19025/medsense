# MedSense

Sistema de gerenciamento de usuários, perfis de saúde e lembretes para clínicas e hospitais, desenvolvido em Python com arquitetura em camadas e aplicação de padrões de projeto (GoF).

---

## Sumário

- [Visão geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Padrões de projeto aplicados](#padrões-de-projeto-aplicados)
- [Diagramas C4](#diagramas-c4)
- [Diagrama de classes](#diagrama-de-classes)
- [Como executar](#como-executar)
- [Como rodar os testes](#como-rodar-os-testes)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Contribuição](#contribuição)

---

## Visão geral

O MedSense permite que clínicas e hospitais gerenciem:

- **Usuários** — familiares de pacientes e responsáveis familiares, com cadastro, listagem e controle de acesso.
- **Perfis de saúde** — tipo sanguíneo, alergias, condições crônicas e medicamentos contínuos, com histórico de alterações e possibilidade de desfazer a última atualização.
- **Lembretes de saúde** — medicamentos, consultas e exames, com notificação automática de observadores a cada mudança de estado.
- **Resumos de saúde** — documentos gerados em texto ou HTML, reunindo dados do usuário, perfil e seções opcionais.

O sistema pode persistir dados em memória RAM, arquivo binário ou banco SQLite, escolhido no início da execução.

## Arquitetura

O projeto segue uma arquitetura em camadas (padrão BCE — Boundary, Control, Entity):

| Camada | Pasta | Responsabilidade |
|---|---|---|
| **Boundary** | `src/boundary/` | Interfaces de linha de comando (entrada e saída de dados) |
| **Control** | `src/control/` | Regras de negócio e orquestração |
| **Entity** | `src/entity/` | Dados e comportamentos das entidades do domínio |
| **Collection** | `src/collection/` | Armazenamento em memória (cache de trabalho) |
| **Infra** | `src/infra/` | Persistência, logging e adapters |

Toda a interação da camada `boundary` com o sistema passa por uma única fachada: `FacadeSingletonController`.

## Padrões de projeto aplicados

| Padrão | Onde | Papel |
|---|---|---|
| **Facade** | `control/facade_singleton_controller.py` | Unifica usuários, perfis, lembretes e resumos numa única interface para a camada de boundary |
| **Singleton** | `control/facade_singleton_controller.py` | Garante uma única instância da fachada durante toda a execução |
| **Command** | `control/comando.py`, `control/comandos_perfil_saude.py`, `control/executor_comandos.py` | Encapsula as operações de perfil de saúde (cadastrar, atualizar, remover) como objetos executáveis |
| **Memento** | `entity/perfil_saude_memento.py`, `control/historico_perfil_saude.py` | Guarda o estado anterior do perfil de saúde, permitindo desfazer a última atualização |
| **Observer** | `control/observadores_lembrete.py`, `control/lembrete_control.py` | Notifica observadores (console, registro) a cada criação, atualização ou conclusão de lembrete |
| **Builder** | `control/resumo_saude_builder.py` | Constrói resumos de saúde em texto ou HTML a partir da mesma receita de passos |
| **Abstract Factory** | `infra/persistencia/fabrica_repositorios.py` | Produz a família completa de repositórios (memória, arquivo, SQLite) sem expor as classes concretas |
| **Adapter** | `infra/logging_adapter.py` | Adapta a biblioteca de logging padrão à porta `Logger` usada pelo sistema |
| **Template Method** | `control/relatorio_acesso.py` | Define o esqueleto da geração de relatórios de acesso, com passos especializados por formato |

Cada padrão tem um ADR (Architecture Decision Record) correspondente em [`docs/adr/`](docs/adr/), documentando o contexto e a decisão de uso.

## Diagramas C4

### Nível 1 — Contexto

```mermaid
C4Context
    title Diagrama de Contexto - MedSense

    Person(familiar, "Familiar Paciente", "Gerencia seus dados de saude e lembretes")
    Person(responsavel, "Responsavel Familiar", "Acompanha e gerencia perfis de pacientes sob sua responsabilidade")

    System(medsense, "MedSense", "Sistema de gerenciamento de usuarios, perfis de saude e lembretes")

    System_Ext(armazenamento, "Mecanismo de Armazenamento", "Memoria RAM, arquivo binario ou banco SQLite")

    Rel(familiar, medsense, "Cadastra dados, perfil de saude e lembretes")
    Rel(responsavel, medsense, "Acompanha perfis e lembretes de pacientes")
    Rel(medsense, armazenamento, "Persiste e recupera dados")
```

### Nível 2 — Contêineres

```mermaid
C4Container
    title Diagrama de Conteineres - MedSense

    Person(usuario, "Usuario", "Familiar Paciente ou Responsavel Familiar")

    Container_Boundary(medsense, "MedSense (aplicacao CLI)") {
        Container(boundary, "Camada Boundary", "Python", "Menus e interfaces de linha de comando")
        Container(facade, "FacadeSingletonController", "Python", "Fachada unica de acesso ao sistema (Facade + Singleton)")
        Container(control, "Camada Control", "Python", "Regras de negocio: usuarios, perfis, lembretes, resumos")
        Container(entity, "Camada Entity", "Python", "Entidades de dominio")
        Container(collection, "Camada Collection", "Python", "Cache de trabalho em memoria")
    }

    ContainerDb(memoria, "Repositorio em Memoria", "Python dict/list", "Sem durabilidade")
    ContainerDb(arquivo, "Repositorio em Arquivo", "Arquivo binario", "Um arquivo por entidade")
    ContainerDb(sqlite, "Repositorio SQLite", "SQLite", "Um banco, uma tabela por entidade")

    Rel(usuario, boundary, "Interage via terminal")
    Rel(boundary, facade, "Chama operacoes")
    Rel(facade, control, "Delega para os controllers")
    Rel(control, entity, "Cria e manipula")
    Rel(control, collection, "Le e escreve no cache")
    Rel(collection, memoria, "Persiste (opcional)")
    Rel(collection, arquivo, "Persiste (opcional)")
    Rel(collection, sqlite, "Persiste (opcional)")
```

### Nível 3 — Componentes (Camada Control)

```mermaid
C4Component
    title Diagrama de Componentes - Camada Control

    Container_Boundary(facade_boundary, "FacadeSingletonController") {
        Component(facade, "Facade", "Classe", "Ponto unico de entrada (Facade + Singleton)")
    }

    Component(usuario_ctrl, "UsuarioControl", "Classe", "CRUD de usuarios e acessos")
    Component(perfil_ctrl, "PerfilSaudeControl", "Classe", "CRUD de perfis de saude")
    Component(lembrete_ctrl, "LembreteControl", "Classe", "CRUD de lembretes (Subject do Observer)")
    Component(executor, "ExecutorComandos", "Classe", "Executa comandos (Command)")
    Component(historico, "HistoricoPerfilSaude", "Classe", "Guarda o memento do ultimo estado (Memento)")
    Component(diretor, "DiretorResumoSaude", "Classe", "Orquestra a construcao de resumos (Builder)")
    Component(observadores, "ObservadorLembrete", "Interface", "Console e Registro de notificacoes")

    Rel(facade, usuario_ctrl, "delega")
    Rel(facade, perfil_ctrl, "delega via Command")
    Rel(facade, lembrete_ctrl, "delega")
    Rel(facade, executor, "usa")
    Rel(facade, historico, "usa")
    Rel(facade, diretor, "usa")
    Rel(executor, perfil_ctrl, "executa comandos sobre")
    Rel(lembrete_ctrl, observadores, "notifica")
    Rel(perfil_ctrl, historico, "salva memento em")
```

## Diagrama de classes

Diagrama de classes com cores por padrão de projeto (Facade/Singleton em azul, Command/Memento em roxo, Observer em verde, Builder em laranja):

```mermaid
classDiagram
    direction TB

    class FacadeSingletonController {
        -_usuario_control UsuarioControl
        -_perfil_saude_control PerfilSaudeControl
        -_lembrete_control LembreteControl
        -_diretor_resumo_saude DiretorResumoSaude
        -_executor_comandos ExecutorComandos
        -_historico_perfil_saude HistoricoPerfilSaude
        $obter_instancia() FacadeSingletonController
        +cadastrar_perfil_saude(email, dados)
        +atualizar_perfil_saude(email, dados)
        +desfazer_ultima_atualizacao_perfil()
        +criar_lembrete(email, dados)
        +gerar_resumo_saude_basico(email)
    }

    class Comando {
        <<interface>>
        +executar()
    }
    class CadastrarPerfilSaudeCommand
    class AtualizarPerfilSaudeCommand
    class RemoverPerfilSaudeCommand
    class ExecutorComandos {
        +executar(comando)
    }
    class PerfilSaudeMemento {
        -estado PerfilSaude
    }
    class HistoricoPerfilSaude {
        +salvar(memento)
        +recuperar() PerfilSaudeMemento
        +limpar()
    }

    class ObservadorLembrete {
        <<interface>>
        +notificar(lembrete, acao)
    }
    class NotificadorConsole
    class RegistroNotificacaoObserver
    class LembreteControl {
        -_observadores List
        +anexar_observador(obs)
        +criar_lembrete(email, dados)
        +listar_lembretes()
    }

    class ResumoSaudeBuilder {
        <<abstract>>
        +construir_cabecalho()
        +construir_dados_usuario(usuario)
        +construir_perfil_saude(perfil)
        +obter_resultado() ResumoSaude
    }
    class ResumoSaudeTextoBuilder
    class ResumoSaudeHTMLBuilder
    class DiretorResumoSaude {
        -_builder ResumoSaudeBuilder
        +construir_resumo_basico(usuario, perfil)
        +construir_resumo_completo(usuario, perfil)
    }

    class PerfilSaudeControl
    class UsuarioControl

    FacadeSingletonController --> ExecutorComandos
    FacadeSingletonController --> HistoricoPerfilSaude
    FacadeSingletonController --> LembreteControl
    FacadeSingletonController --> DiretorResumoSaude
    FacadeSingletonController --> UsuarioControl
    FacadeSingletonController --> PerfilSaudeControl

    Comando <|.. CadastrarPerfilSaudeCommand
    Comando <|.. AtualizarPerfilSaudeCommand
    Comando <|.. RemoverPerfilSaudeCommand
    ExecutorComandos ..> Comando : executa
    AtualizarPerfilSaudeCommand ..> HistoricoPerfilSaude : salva memento
    HistoricoPerfilSaude o-- PerfilSaudeMemento
    AtualizarPerfilSaudeCommand ..> PerfilSaudeControl

    ObservadorLembrete <|.. NotificadorConsole
    ObservadorLembrete <|.. RegistroNotificacaoObserver
    LembreteControl o-- ObservadorLembrete : notifica

    ResumoSaudeBuilder <|-- ResumoSaudeTextoBuilder
    ResumoSaudeBuilder <|-- ResumoSaudeHTMLBuilder
    DiretorResumoSaude o-- ResumoSaudeBuilder

    style FacadeSingletonController fill:#2b5b84,color:#fff
    style CadastrarPerfilSaudeCommand fill:#5b3a8c,color:#fff
    style AtualizarPerfilSaudeCommand fill:#5b3a8c,color:#fff
    style RemoverPerfilSaudeCommand fill:#5b3a8c,color:#fff
    style ExecutorComandos fill:#5b3a8c,color:#fff
    style Comando fill:#5b3a8c,color:#fff
    style PerfilSaudeMemento fill:#5b3a8c,color:#fff
    style HistoricoPerfilSaude fill:#5b3a8c,color:#fff
    style ObservadorLembrete fill:#2f7d4f,color:#fff
    style NotificadorConsole fill:#2f7d4f,color:#fff
    style RegistroNotificacaoObserver fill:#2f7d4f,color:#fff
    style LembreteControl fill:#2f7d4f,color:#fff
    style ResumoSaudeBuilder fill:#b5651d,color:#fff
    style ResumoSaudeTextoBuilder fill:#b5651d,color:#fff
    style ResumoSaudeHTMLBuilder fill:#b5651d,color:#fff
    style DiretorResumoSaude fill:#b5651d,color:#fff
```

> O diagrama de classes de análise completo (com as camadas Boundary, Control e Entity antes da aplicação dos padrões finais) está disponível em [`docs/classes-analise/`](docs/classes-analise/).

## Como executar

```bash
git clone https://github.com/diogo19025/medsense.git
cd medsense
python src/main.py
```

O sistema pergunta o mecanismo de armazenamento (memória, arquivo ou SQLite) e em seguida exibe o menu principal.

## Como rodar os testes

```bash
cd tests
python -m unittest discover -v
```

Ou individualmente:

```bash
python test_facade_singleton_controller.py
```

## Estrutura de pastas

```
medsense/
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   └── classes-analise/      # Diagramas de análise (BCE)
├── src/
│   ├── boundary/              # Interfaces de linha de comando
│   ├── collection/            # Cache em memória
│   ├── control/                # Regras de negócio e padrões
│   ├── entity/                  # Entidades de domínio
│   └── infra/
│       └── persistencia/     # Repositórios (memória, arquivo, SQLite)
└── tests/                     # Testes unitários e de integração
```

## Contribuição

As práticas de branches, commits e pull requests do projeto estão documentadas em [`CONTRIBUTING.md`](CONTRIBUTING.md).