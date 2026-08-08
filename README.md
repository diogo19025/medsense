# MedSense

Sistema de gestão familiar de saúde desenvolvido em Python, com interface de linha de comando, arquitetura em camadas e aplicação de padrões de projeto (GoF).

---

## Sumário

- [Visão geral](#visão-geral)
- [Repositório](#repositório)
- [Documentação](#documentação)
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

O MedSense permite organizar informações de saúde de familiares:

- **Usuários** — familiares de pacientes e responsáveis familiares, com cadastro, listagem e controle de acesso.
- **Perfis de saúde** — tipo sanguíneo, alergias, condições crônicas e medicamentos contínuos, com histórico de alterações e possibilidade de desfazer a última atualização.
- **Lembretes de saúde** — medicamentos, consultas e exames, com criação, atualização, conclusão, cancelamento e remoção, notificando os observadores a cada mudança de estado.
- **Resumos de saúde** — documentos gerados em texto ou HTML, reunindo dados do usuário, perfil e seções opcionais.

Usuários, acessos e perfis de saúde podem ser persistidos em memória RAM, arquivo binário ou banco SQLite, escolhido no início da execução. Lembretes e resumos não têm repositório: os lembretes vivem apenas na coleção em RAM durante a execução, e os resumos são gerados sob demanda em arquivo (`resumo_saude.txt`/`.html`).

## Repositório

[https://github.com/diogo19025/medsense](https://github.com/diogo19025/medsense)

## Documentação

- [Documento de Requisitos de Software](docs/MedSense_Documento_Requisitos_Revisado.pdf)
- [Índice da documentação](docs/README.md)
- [Decisões arquiteturais](docs/adr/)
- [Diagrama de casos de uso](docs/casos-de-uso/DiagramaCasosDeUso.jpg)
- [Diagramas de classes de análise](docs/classes-analise/)

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

![Diagrama C4 de contexto do MedSense](docs/arquitetura/c4-nivel-1-contexto.png)

### Nível 2 — Contêineres

![Diagrama C4 de contêineres do MedSense](docs/arquitetura/c4-nivel-2-conteineres.png)

### Nível 3 — Componentes (Camada Control)

![Diagrama C4 de componentes da camada Control](docs/arquitetura/c4-nivel-3-componentes.png)

## Diagrama de classes

Os diagramas oficiais foram divididos em duas partes para preservar a legibilidade das classes, relacionamentos e padrões.

### Padrões comportamentais e de criação na camada Control

![Diagrama de classes dos padrões da camada Control](docs/arquitetura/classes-padroes-control.png)

### Persistência, logging e relatórios

![Diagrama de classes de persistência, logging e relatórios](docs/arquitetura/classes-persistencia-logging-relatorios.png)

### Visão resumida em Mermaid

O modelo abaixo oferece uma visão textual complementar dos principais padrões comportamentais e de criação:

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
        +concluir_lembrete(id)
        +cancelar_lembrete(id)
        +remover_lembrete(id)
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
    RemoverPerfilSaudeCommand ..> HistoricoPerfilSaude : descarta memento
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
│   ├── adr/                   # Architecture Decision Records
│   ├── arquitetura/           # Diagramas C4 e diagramas de classes finais
│   ├── casos-de-uso/          # Diagrama de casos de uso
│   ├── classes-analise/       # Diagramas de análise (BCE)
│   ├── README.md              # Índice dos artefatos de documentação
│   └── MedSense_Documento_Requisitos_Revisado.pdf
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

As práticas de branches, commits e pull requests do projeto estão documentadas em [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).
