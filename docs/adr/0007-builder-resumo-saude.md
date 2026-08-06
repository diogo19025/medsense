# ADR-0007: Builder para o resumo de saúde

- Status: Aceito
- Data: 2026-08-06

## Contexto

O Laboratório exige (item "Builder") identificar e implementar um cenário de
uso do padrão Builder na camada de negócio.

O sistema já reúne, espalhados por entidades diferentes, todos os dados que
compõem a visão clínica de um paciente: a identificação vem do `Usuario`
(`FamiliarPaciente`) e as informações clínicas do `PerfilSaude` (ADR-0006).
Não havia, porém, nenhuma forma de apresentar isso como um documento único.

Esse documento tem duas características que pedem o Builder:

- é montado **por partes** — cabeçalho, dados do usuário, perfil de saúde e
  seções que podem ou não existir (medicamentos, vacinas, consultas e
  documentos);
- precisa sair em **mais de uma representação** (texto puro e HTML), sem que
  a receita de montagem seja reescrita por formato.

O ADR-0004 já resolveu um problema parecido nos relatórios de acesso com
**Template Method**, mas ali o algoritmo é fixo e vive na classe base. Aqui a
composição varia por chamada: dois resumos do mesmo formato podem ter conjuntos
de seções diferentes. Quem varia a composição é o cliente, não a subclasse — o
que caracteriza Builder, e não Template Method.

## Decisão

1. Criar a entidade `ResumoSaude` (`src/entity/resumo_saude.py`) como **produto**
   da construção: dataclass congelada com `usuario_id`, `formato`, `conteudo`,
   `secoes` e `gerado_em`. Congelada porque um documento gerado não é editado
   depois, seguindo o precedente de `RegistroAcesso` (ADR-0004). O vínculo com
   o dono é feito por `usuario_id`, pelo mesmo motivo do ADR-0006, decisão 1.
2. Registrar em `secoes`, na ordem de montagem, o nome das seções que
   entraram no documento. É o que torna a opcionalidade observável sem
   precisar interpretar o texto de `conteudo`.
3. Definir o **builder abstrato** `ResumoSaudeBuilder`
   (`src/control/resumo_saude_builder.py`) com um passo por seção
   (`construir_cabecalho`, `construir_dados_usuario`, `construir_perfil_saude`,
   `construir_medicamentos`, `construir_vacinas`, `construir_consultas`,
   `construir_documentos`, `construir_rodape`). Os passos devolvem `self`,
   permitindo encadeamento, e a base concentra o que não depende de formato:
   `reiniciar()`, o registro das seções e `obter_resultado()`.
4. `obter_resultado()` entrega o `ResumoSaude` e **reinicia** o builder, para
   que uma segunda construção nunca herde as seções da primeira.
5. Fornecer dois **builders concretos**: `ResumoSaudeTextoBuilder` e
   `ResumoSaudeHTMLBuilder`, reaproveitando as convenções de saída já
   adotadas nos relatórios do ADR-0004 (texto sem acentos, HTML com entidades
   e `html.escape` no conteúdo vindo do usuário). Um formato novo (ex.: PDF) é
   apenas mais um builder.
6. Manter a **ordem** dos passos fora dos builders, no `DiretorResumoSaude`,
   com duas receitas: `construir_resumo_basico` (usuário + perfil) e
   `construir_resumo_completo` (a básica acrescida das seções opcionais). O
   diretor não conhece o formato: trocar o builder troca a saída sem tocar na
   receita. É essa separação que diferencia a solução do Template Method do
   ADR-0004.
7. Tratar medicamentos, vacinas, consultas e documentos como **seções
   opcionais**: quando a lista chega vazia, o passo não acrescenta nada ao
   documento nem à lista de seções.
8. Aceitar `perfil=None` na construção, para que um paciente ainda sem perfil
   de saúde cadastrado também tenha resumo — a seção é montada com um aviso.

### Papéis do padrão

| Papel do Builder | Elemento no projeto                                      |
|------------------|----------------------------------------------------------|
| Builder          | `ResumoSaudeBuilder` (ABC)                               |
| ConcreteBuilder  | `ResumoSaudeTextoBuilder`, `ResumoSaudeHTMLBuilder`      |
| Director         | `DiretorResumoSaude`                                     |
| Product          | `ResumoSaude` (entidade)                                 |

## Consequências

- A composição do resumo passa a ser decidida por chamada, sem multiplicar
  classes: as combinações de seções opcionais não viram subclasses.
- Acrescentar um formato é escrever um builder; acrescentar uma receita é
  escrever um método no diretor. As duas dimensões variam de forma
  independente.
- As seções opcionais recebem os itens já prontos como `list[str]`. As
  entidades de medicamentos, vacinas, consultas e documentos ainda não existem
  no projeto; quando existirem, só os passos correspondentes mudam — a receita
  do diretor e o produto continuam valendo.
- O resumo ainda não é oferecido na CLI: esta decisão cobre apenas a camada de
  negócio, e a integração com `boundary` fica para quando houver um item de
  menu definido.
- O diagrama de classes deve passar a exibir `ResumoSaude`,
  `ResumoSaudeBuilder` e suas duas implementações e `DiretorResumoSaude`, com a
  marcação «Builder».

## Referências

- ADR-0004: Template Method para relatórios de acesso (padrão vizinho, com a
  distinção discutida no contexto).
- ADR-0006: CRUD de Perfil de Saúde (origem dos dados clínicos do resumo).
