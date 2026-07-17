# ADR-0006: CRUD de Perfil de Saúde

- Status: Aceito
- Data: 2026-07-16

## Contexto

O diagrama de classes (estado atual) prevê a entidade `PerfilSaude` em
composição 1:1 com `FamiliarPaciente`, com os campos `tipo_sanguineo`,
`alergias`, `condicoes_cronicas`, `medicamentos_continuos` e
`observacoes`, mas ela ainda não existia no código. Era necessário
implementar o CRUD completo (cadastrar, buscar, listar, atualizar e
remover), respeitando os padrões já adotados: validação na entidade
(ADR-0001), persistência com desfazer-em-falha (ADR-0002), log via porta
`Logger` (ADR-0003) e Repository com Abstract Factory (ADR-0005).

## Decisão

1. Criar a entidade `PerfilSaude` (`src/entity`) com os campos do
   diagrama, vinculada ao dono pelo `usuario_id` — a referência por id,
   em vez de objeto aninhado, mantém a entidade serializável pelos três
   mecanismos e segue o precedente de `RegistroAcesso`. A validação
   (tipo sanguíneo ABO/Rh, vínculo obrigatório) vive no
   `ValidadorPerfilSaude` e dispara em `__post_init__`, com a exceção de
   domínio `PerfilSaudeInvalidoError`.
2. Manter a cardinalidade da composição do diagrama na
   `PerfilSaudeCollection`: no máximo um perfil por usuário; a coleção
   também oferece `atualizar`, substituindo o perfil do mesmo usuário.
3. Resolver o dono do perfil em `PerfilSaudeControl` pelo email, através
   do novo método público `UsuarioControl.buscar_usuario_por_email`,
   exigindo que seja um `FamiliarPaciente` — apenas pacientes possuem
   perfil de saúde.
4. Atualização parcial: `atualizar_perfil(email, dados)` altera somente
   os campos presentes em `dados`, preservando os demais e o `id` do
   perfil (a identidade sobrevive à atualização nos meios duráveis).
5. Seguir o ADR-0005 na persistência: contrato `RepositorioPerfilSaude`
   em `src/collection` e três implementações em `src/infra/persistencia`
   (memória, arquivo binário e SQLite). **Estender o contrato público
   `FabricaRepositorios`** com `criar_repositorio_perfis_saude()` em
   todas as famílias — mudança de contrato registrada por este ADR,
   conforme a regra 3 do `CONTRIBUTING.md`.
6. No SQLite, serializar as listas do perfil em JSON (módulo `json` da
   stdlib), pois o banco não possui tipo de coluna de lista; a tabela
   `perfis_saude` compartilha o arquivo de banco da família e impõe
   `UNIQUE` em `usuario_id`, espelhando a decisão 2.
7. Espelhar toda mudança (cadastro, atualização e remoção) no
   repositório durável com desfazer-em-falha (ADR-0002, decisão 5) —
   inclusive nas operações novas: a atualização restaura o perfil
   anterior e a remoção readiciona o perfil quando a persistência falha.

## Consequências

- O CRUD fica disponível na CLI pela `PerfilSaudeView` (submenu do menu
  principal), sem que boundary e control conheçam o mecanismo de
  armazenamento.
- Quem implementar uma nova família de repositórios passa a precisar
  fornecer também o repositório de perfis de saúde.
- O diagrama de classes deve passar a exibir `PerfilSaudeCollection`,
  `PerfilSaudeControl`, `PerfilSaudeView`, `RepositorioPerfilSaude` e
  suas três implementações.

## Referências

- ADR-0001: validação de campos no cadastro de usuário.
- ADR-0002: persistência de usuários e tratamento de exceções.
- ADR-0003: Adapter para biblioteca de log.
- ADR-0005: Repository na camada infra com Abstract Factory.
