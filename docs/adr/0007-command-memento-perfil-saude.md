# ADR-0007: Command e Memento no perfil de saúde

- Status: Aceito
- Data: 2026-08-06

## Contexto

O projeto final exige aplicar os padrões Command e Memento às operações de
perfil de saúde. Até esta decisão, a `FacadeSingletonController` delegava
cadastro, atualização e remoção diretamente ao `PerfilSaudeControl`, e não
existia uma forma de desfazer uma alteração clínica.

O CRUD definido no ADR-0006 já concentra no controle as regras de negócio e a
coordenação entre a coleção em RAM e o Repository. A nova solução deve preservar
essas responsabilidades, manter as assinaturas públicas existentes e permitir
desfazer somente a atualização mais recente, inclusive nos mecanismos duráveis.

## Decisão

### Command

Adotar o contrato `Comando`, com o método `executar()`, e encapsular cada
operação mutável de perfil nas classes `CadastrarPerfilSaudeCommand`,
`AtualizarPerfilSaudeCommand` e `RemoverPerfilSaudeCommand`.

Os participantes são:

| Papel | Elemento no projeto |
|---|---|
| Command | `Comando` |
| Concrete Command | `CadastrarPerfilSaudeCommand` |
| Concrete Command | `AtualizarPerfilSaudeCommand` |
| Concrete Command | `RemoverPerfilSaudeCommand` |
| Receiver | `PerfilSaudeControl` |
| Invoker | `ExecutorComandos` |
| Client | `FacadeSingletonController` |

Os comandos apenas coordenam e delegam. Validação, cardinalidade, atualização
parcial, logs e persistência continuam no Receiver, sem duplicação de regras de
negócio. A fachada preserva os métodos públicos de cadastro, atualização e
remoção, mas passa a criar os comandos e enviá-los ao executor.

### Memento

Adotar `PerfilSaude` como Originator, `PerfilSaudeMemento` como Memento e
`HistoricoPerfilSaude` como Caretaker. O Originator cria um retrato contendo
`id`, `usuario_id`, `tipo_sanguineo`, `alergias`, `condicoes_cronicas`,
`medicamentos_continuos` e `observacoes`.

As listas são copiadas para tuplas no retrato, tornando o estado armazenado
imutável. Ao restaurar, novas listas são criadas, impedindo que alterações
posteriores no perfil modifiquem o Memento. O Originator também verifica se a
identidade do retrato corresponde ao mesmo `id` e `usuario_id`.

O `AtualizarPerfilSaudeCommand` segue este fluxo:

1. busca o perfil atual no Receiver;
2. cria o Memento antes da alteração;
3. solicita a atualização ao `PerfilSaudeControl`;
4. guarda o Memento somente depois que a atualização e a persistência terminam
   com sucesso.

O `RemoverPerfilSaudeCommand` também recebe o Caretaker. Depois que a remoção é
confirmada pelo Receiver, ele compara o `id` do perfil removido com o do retrato
guardado e só descarta quando são o mesmo. Sem o Originator não há o que
restaurar: manter o retrato deixaria o desfazer preso num erro de identidade
pelo resto da execução, inclusive depois de o paciente cadastrar um perfil novo.
A comparação é necessária porque o Caretaker é único para todo o sistema —
remover o perfil de um paciente não pode apagar o desfazer pendente de outro.

O Caretaker mantém uma única referência. Uma nova atualização bem-sucedida
substitui o retrato anterior, pois o requisito permite desfazer somente a última
atualização e não exige uma pilha de versões. Isso reduz estado e torna explícito
que a funcionalidade não é um histórico clínico nem uma trilha de auditoria.

## Funcionamento do desfazer

A fachada oferece `desfazer_ultima_atualizacao_perfil()`. Ela recupera o último
Memento e solicita ao `PerfilSaudeControl` que restaure e persista o perfil. O
controle usa o mesmo mecanismo de espelhamento e rollback do ADR-0002: se a
gravação falhar, restaura em RAM o estado que estava vigente antes da tentativa.

O Caretaker só é limpo após a persistência bem-sucedida — ou quando o perfil dono
do retrato é removido, conforme descrito acima. Assim, uma falha de gravação
mantém RAM e armazenamento durável no estado atualizado e permite repetir o
desfazer. Depois de um desfazer concluído, uma nova tentativa produz um erro
claro porque não há mais estado disponível.

## Impactos

### FacadeSingletonController

- As assinaturas públicas existentes de cadastro, atualização e remoção foram
  preservadas.
- Foi acrescentado o método público de desfazer a última atualização.
- A fachada passa a possuir o executor e o histórico de perfil, mantendo uma
  interface simples para a boundary.
- `AtualizarPerfilSaudeCommand` e `RemoverPerfilSaudeCommand` recebem o Caretaker
  na construção; a fachada, como Client, é quem o injeta.

### Persistência

- Não há novo formato de armazenamento nem nova dependência.
- A restauração reutiliza `RepositorioPerfilSaude` e persiste a coleção completa,
  portanto funciona com memória, arquivo binário e SQLite.
- Em falha de gravação, o estado em RAM volta ao estado ainda existente no
  repositório, e o Memento permanece disponível para uma nova tentativa.

### Requisito de atualização do perfil

A atualização parcial definida no ADR-0006 continua inalterada. Command passa a
encapsular a solicitação, enquanto Memento acrescenta reversibilidade à última
alteração sem mudar validações, identidade ou vínculo do perfil com o usuário.

## Consequências

### Positivas

- operações mutáveis passam a ter representação uniforme e extensível;
- a fachada deixa de acionar diretamente as mutações de perfil;
- a última atualização pode ser desfeita com cópias defensivas;
- a restauração respeita a consistência entre RAM e Repository;
- os contratos públicos anteriores permanecem compatíveis.

### Negativas

- há mais classes para uma operação antes feita por delegação direta;
- apenas uma atualização pode ser desfeita e o estado não sobrevive ao processo;
- remover o perfil depois de atualizá-lo impede restaurar aquele Memento, pois o
  Originator correspondente não existe mais; o desfazer passa a responder que não
  há atualização a desfazer, em vez de falhar por identidade;
- o Caretaker único obriga o comando de remoção a conhecer o retrato guardado
  para decidir se ele ainda faz sentido.

## Referências

- ADR-0002: persistência e tratamento de exceções.
- ADR-0005: Repository e Abstract Factory.
- ADR-0006: CRUD de Perfil de Saúde.
