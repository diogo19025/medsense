# ADR-0004: Template Method para relatórios de acesso

- Status: Aceito
- Data: 2026-07-13

## Contexto

O Laboratório exige (item "Template Method") implementar, na camada de
negócio, a geração de mais um tipo de relatório (por exemplo, HTML e PDF),
gerando estatísticas de acesso dos usuários no sistema.

O sistema não registrava acessos. O algoritmo de geração de um relatório é o
mesmo em todos os formatos — calcular as estatísticas e montar as seções na
mesma ordem —, variando apenas a formatação de saída. Duplicar esse fluxo por
formato levaria a repetição e a divergência de conteúdo entre formatos.

## Decisão

1. Registrar acessos com a entidade `RegistroAcesso` (`src/entity`) e a coleção
   em memória `AcessoCollection` (`src/collection`). `UsuarioControl` ganha
   `registrar_acesso(email, acao)` e `gerar_relatorio_acessos(formato)`.
2. Aplicar **Template Method** na classe abstrata `RelatorioAcesso`
   (`src/control/relatorio_acesso.py`):
   - `gerar()` é o **template method** invariante: calcula as estatísticas
     (`_calcular_estatisticas`, passo concreto comum) e monta as seções na
     ordem fixa (cabeçalho → resumo → por usuário → rodapé → montagem).
   - As *primitive operations* (`_cabecalho`, `_secao_resumo`,
     `_secao_por_usuario`, `_rodape`, `_montar`, `extensao`) são abstratas e
     implementadas por cada formato.
3. Fornecer duas subclasses concretas: `RelatorioAcessoTexto` e
   `RelatorioAcessoHTML`. Um novo formato (ex.: `RelatorioAcessoPDF`) é apenas
   mais uma subclasse.
4. As estatísticas incluem: total de acessos, usuários distintos, acessos por
   login, acessos por tipo de usuário, primeiro/último acesso e usuário mais
   ativo (`EstatisticasAcesso`).

## Consequências

- O algoritmo e as estatísticas ficam definidos uma única vez na base; as
  subclasses não conseguem divergir no conteúdo, só no formato.
- PDF não foi implementado para não introduzir dependência externa (ex.:
  `reportlab`), conforme a regra 6 do `CONTRIBUTING.md`. A estrutura deixa a
  adição trivial como subclasse futura.
- O relatório usa o mesmo `Logger` (ADR-0003) para registrar sua geração.
- O diagrama de classes deve exibir `RelatorioAcesso` e suas subclasses com a
  marcação «Template Method».

## Referências

- ADR-0002: persistência de usuários e tratamento de exceções.
- ADR-0003: Adapter para biblioteca de log.
