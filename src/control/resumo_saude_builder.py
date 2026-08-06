from abc import ABC, abstractmethod
from datetime import datetime
from html import escape

from entity.perfil_saude import PerfilSaude
from entity.resumo_saude import ResumoSaude
from entity.usuario import Usuario

# Nomes das seções do resumo. Servem de identificador independente de
# formato: é o que fica registrado em `ResumoSaude.secoes`, enquanto cada
# builder decide como escrever o título na sua saída.
SECAO_DADOS_USUARIO = "Dados do usuario"
SECAO_PERFIL_SAUDE = "Perfil de saude"
SECAO_MEDICAMENTOS = "Medicamentos"
SECAO_VACINAS = "Vacinas"
SECAO_CONSULTAS = "Consultas"
SECAO_DOCUMENTOS = "Documentos"

SEM_INFORMACAO = "-"
SEM_PERFIL = "Paciente ainda nao possui perfil de saude."


# Junta os itens numa linha só, exibindo "-" quando a lista está vazia.
def _juntar(itens: list[str]) -> str:
    return ", ".join(itens) if itens else SEM_INFORMACAO


class ResumoSaudeBuilder(ABC):
    """Construtor de resumos de saúde (padrão Builder).

    Declara os passos de construção do documento — um por seção — sem
    fixar a representação final: cada builder concreto executa os mesmos
    passos num formato de saída diferente (texto puro, HTML e, futuramente,
    PDF). A **ordem** dos passos não é definida aqui, e sim pelo
    `DiretorResumoSaude`, que é o que distingue este padrão do Template
    Method usado nos relatórios de acesso (ADR-0004).

    Os passos devolvem `self`, permitindo encadeamento, e
    `obter_resultado()` entrega o `ResumoSaude` pronto e reinicia o
    builder, deixando-o livre para montar o próximo documento.
    """

    def __init__(self):
        self.reiniciar()

    # Descarta o documento em construção e prepara o builder para o próximo.
    def reiniciar(self) -> "ResumoSaudeBuilder":
        self._usuario_id = ""
        self._partes: list[str] = []
        self._secoes: list[str] = []
        return self

    # -------- Produto em construção --------

    # Entrega o resumo pronto e reinicia o builder, para que uma segunda
    # construção nunca herde as seções da primeira.
    def obter_resultado(self) -> ResumoSaude:
        resumo = ResumoSaude(
            usuario_id=self._usuario_id,
            formato=self.formato,
            conteudo=self._montar(self._partes),
            secoes=tuple(self._secoes),
        )
        self.reiniciar()
        return resumo

    # -------- Passos de construção (formato-específicos) --------

    @property
    @abstractmethod
    # Nome do formato produzido pelo builder (ex.: "texto", "html").
    def formato(self) -> str: ...

    @abstractmethod
    # Abre o documento com o título do resumo.
    def construir_cabecalho(self) -> "ResumoSaudeBuilder": ...

    @abstractmethod
    # Seção de identificação do dono do resumo.
    def construir_dados_usuario(self, usuario: Usuario) -> "ResumoSaudeBuilder": ...

    @abstractmethod
    # Seção com as informações clínicas do perfil de saúde.
    def construir_perfil_saude(
        self, perfil: PerfilSaude | None
    ) -> "ResumoSaudeBuilder": ...

    @abstractmethod
    # Seção opcional de medicamentos.
    def construir_medicamentos(
        self, medicamentos: list[str]
    ) -> "ResumoSaudeBuilder": ...

    @abstractmethod
    # Seção opcional de vacinas.
    def construir_vacinas(self, vacinas: list[str]) -> "ResumoSaudeBuilder": ...

    @abstractmethod
    # Seção opcional de consultas.
    def construir_consultas(self, consultas: list[str]) -> "ResumoSaudeBuilder": ...

    @abstractmethod
    # Seção opcional de documentos.
    def construir_documentos(self, documentos: list[str]) -> "ResumoSaudeBuilder": ...

    @abstractmethod
    # Fecha o documento com a data de geração.
    def construir_rodape(self) -> "ResumoSaudeBuilder": ...

    @abstractmethod
    # Junta as partes construídas no documento final do formato.
    def _montar(self, partes: list[str]) -> str: ...

    # -------- Utilitários comuns a todos os formatos --------

    # Acrescenta um trecho que não é seção de conteúdo (cabeçalho, rodapé).
    def _adicionar_parte(self, texto: str) -> "ResumoSaudeBuilder":
        self._partes.append(texto)
        return self

    # Acrescenta uma seção de conteúdo, registrando o nome na ordem de
    # montagem para que o resumo saiba o que foi incluído.
    def _adicionar_secao(self, nome: str, texto: str) -> "ResumoSaudeBuilder":
        self._secoes.append(nome)
        return self._adicionar_parte(texto)

    @staticmethod
    def _formatar_momento(momento: datetime) -> str:
        return momento.strftime("%d/%m/%Y %H:%M:%S")


class ResumoSaudeTextoBuilder(ResumoSaudeBuilder):
    """Constrói o resumo de saúde em texto puro (console/arquivo .txt)."""

    TITULO = "MedSense - Resumo de Saude"

    @property
    def formato(self) -> str:
        return "texto"

    def construir_cabecalho(self) -> "ResumoSaudeBuilder":
        return self._adicionar_parte(f"{self.TITULO}\n{'=' * len(self.TITULO)}")

    def construir_dados_usuario(self, usuario: Usuario) -> "ResumoSaudeBuilder":
        self._usuario_id = usuario.id
        return self._adicionar_secao(
            SECAO_DADOS_USUARIO,
            f"{SECAO_DADOS_USUARIO}\n"
            f"  Nome...: {usuario.nome}\n"
            f"  Login..: {usuario.login}\n"
            f"  Email..: {usuario.email}\n"
            f"  Tipo...: {usuario.tipo_usuario}",
        )

    def construir_perfil_saude(
        self, perfil: PerfilSaude | None
    ) -> "ResumoSaudeBuilder":
        if perfil is None:
            return self._adicionar_secao(
                SECAO_PERFIL_SAUDE, f"{SECAO_PERFIL_SAUDE}\n  {SEM_PERFIL}"
            )
        return self._adicionar_secao(
            SECAO_PERFIL_SAUDE,
            f"{SECAO_PERFIL_SAUDE}\n"
            f"  Tipo sanguineo........: {perfil.tipo_sanguineo}\n"
            f"  Alergias..............: {_juntar(perfil.alergias)}\n"
            f"  Condicoes cronicas....: {_juntar(perfil.condicoes_cronicas)}\n"
            f"  Medicamentos continuos: {_juntar(perfil.medicamentos_continuos)}\n"
            f"  Observacoes...........: {perfil.observacoes or SEM_INFORMACAO}",
        )

    def construir_medicamentos(self, medicamentos: list[str]) -> "ResumoSaudeBuilder":
        return self._construir_lista(SECAO_MEDICAMENTOS, medicamentos)

    def construir_vacinas(self, vacinas: list[str]) -> "ResumoSaudeBuilder":
        return self._construir_lista(SECAO_VACINAS, vacinas)

    def construir_consultas(self, consultas: list[str]) -> "ResumoSaudeBuilder":
        return self._construir_lista(SECAO_CONSULTAS, consultas)

    def construir_documentos(self, documentos: list[str]) -> "ResumoSaudeBuilder":
        return self._construir_lista(SECAO_DOCUMENTOS, documentos)

    # Seção opcional: sem itens, nada é acrescentado ao resumo.
    def _construir_lista(self, nome: str, itens: list[str]) -> "ResumoSaudeBuilder":
        if not itens:
            return self
        linhas = [nome] + [f"  - {item}" for item in itens]
        return self._adicionar_secao(nome, "\n".join(linhas))

    def construir_rodape(self) -> "ResumoSaudeBuilder":
        return self._adicionar_parte(
            f"Gerado em {self._formatar_momento(datetime.now())}"
        )

    def _montar(self, partes: list[str]) -> str:
        return "\n\n".join(partes) + "\n"


class ResumoSaudeHTMLBuilder(ResumoSaudeBuilder):
    """Constrói o resumo de saúde em HTML (navegador/arquivo .html)."""

    @property
    def formato(self) -> str:
        return "html"

    def construir_cabecalho(self) -> "ResumoSaudeBuilder":
        return self._adicionar_parte(
            "<h1>MedSense &ndash; Resumo de Sa&uacute;de</h1>"
        )

    def construir_dados_usuario(self, usuario: Usuario) -> "ResumoSaudeBuilder":
        self._usuario_id = usuario.id
        return self._adicionar_secao(
            SECAO_DADOS_USUARIO,
            "<h2>Dados do usu&aacute;rio</h2>\n<ul>\n"
            f"  <li>Nome: <strong>{escape(usuario.nome)}</strong></li>\n"
            f"  <li>Login: {escape(usuario.login)}</li>\n"
            f"  <li>E-mail: {escape(usuario.email)}</li>\n"
            f"  <li>Tipo: {escape(usuario.tipo_usuario)}</li>\n"
            "</ul>",
        )

    def construir_perfil_saude(
        self, perfil: PerfilSaude | None
    ) -> "ResumoSaudeBuilder":
        if perfil is None:
            return self._adicionar_secao(
                SECAO_PERFIL_SAUDE,
                f"<h2>Perfil de sa&uacute;de</h2>\n<p>{escape(SEM_PERFIL)}</p>",
            )
        return self._adicionar_secao(
            SECAO_PERFIL_SAUDE,
            "<h2>Perfil de sa&uacute;de</h2>\n<ul>\n"
            f"  <li>Tipo sangu&iacute;neo: <strong>{escape(perfil.tipo_sanguineo)}</strong></li>\n"
            f"  <li>Alergias: {escape(_juntar(perfil.alergias))}</li>\n"
            f"  <li>Condi&ccedil;&otilde;es cr&ocirc;nicas: {escape(_juntar(perfil.condicoes_cronicas))}</li>\n"
            f"  <li>Medicamentos cont&iacute;nuos: {escape(_juntar(perfil.medicamentos_continuos))}</li>\n"
            f"  <li>Observa&ccedil;&otilde;es: {escape(perfil.observacoes or SEM_INFORMACAO)}</li>\n"
            "</ul>",
        )

    def construir_medicamentos(self, medicamentos: list[str]) -> "ResumoSaudeBuilder":
        return self._construir_lista(SECAO_MEDICAMENTOS, medicamentos)

    def construir_vacinas(self, vacinas: list[str]) -> "ResumoSaudeBuilder":
        return self._construir_lista(SECAO_VACINAS, vacinas)

    def construir_consultas(self, consultas: list[str]) -> "ResumoSaudeBuilder":
        return self._construir_lista(SECAO_CONSULTAS, consultas)

    def construir_documentos(self, documentos: list[str]) -> "ResumoSaudeBuilder":
        return self._construir_lista(SECAO_DOCUMENTOS, documentos)

    # Seção opcional: sem itens, nada é acrescentado ao resumo.
    def _construir_lista(self, nome: str, itens: list[str]) -> "ResumoSaudeBuilder":
        if not itens:
            return self
        linhas = [f"<h2>{escape(nome)}</h2>", "<ul>"]
        linhas.extend(f"  <li>{escape(item)}</li>" for item in itens)
        linhas.append("</ul>")
        return self._adicionar_secao(nome, "\n".join(linhas))

    def construir_rodape(self) -> "ResumoSaudeBuilder":
        return self._adicionar_parte(
            f"<footer>Gerado em {self._formatar_momento(datetime.now())}</footer>"
        )

    def _montar(self, partes: list[str]) -> str:
        corpo = "\n".join(partes)
        return (
            "<!DOCTYPE html>\n"
            '<html lang="pt-br">\n<head>\n'
            '  <meta charset="utf-8">\n'
            "  <title>MedSense - Resumo de Saude</title>\n"
            "</head>\n<body>\n"
            f"{corpo}\n"
            "</body>\n</html>\n"
        )


class DiretorResumoSaude:
    """Diretor do padrão Builder para resumos de saúde.

    Conhece a **ordem** em que os passos de construção devem ser chamados —
    e só isso. Não conhece o formato de saída: recebe qualquer
    `ResumoSaudeBuilder` e monta, com a mesma receita, um resumo em texto ou
    em HTML. Trocar o builder troca o formato sem tocar na receita.

    Oferece duas receitas: `construir_resumo_basico`, com a identificação do
    usuário e o perfil de saúde, e `construir_resumo_completo`, que acrescenta
    as seções opcionais informadas.
    """

    def __init__(self, builder: ResumoSaudeBuilder):
        self._builder = builder

    # Builder em uso; trocá-lo muda o formato dos próximos resumos.
    @property
    def builder(self) -> ResumoSaudeBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: ResumoSaudeBuilder) -> None:
        self._builder = builder

    # Receita mínima: identificação do usuário e perfil de saúde.
    def construir_resumo_basico(
        self, usuario: Usuario, perfil: PerfilSaude | None
    ) -> ResumoSaude:
        self._builder.reiniciar()
        self._builder.construir_cabecalho()
        self._builder.construir_dados_usuario(usuario)
        self._builder.construir_perfil_saude(perfil)
        self._builder.construir_rodape()
        return self._builder.obter_resultado()

    # Receita completa: a mínima acrescida das seções opcionais. Cada seção
    # opcional só entra no documento quando há itens para ela.
    def construir_resumo_completo(
        self,
        usuario: Usuario,
        perfil: PerfilSaude | None,
        *,
        medicamentos: list[str] | None = None,
        vacinas: list[str] | None = None,
        consultas: list[str] | None = None,
        documentos: list[str] | None = None,
    ) -> ResumoSaude:
        self._builder.reiniciar()
        self._builder.construir_cabecalho()
        self._builder.construir_dados_usuario(usuario)
        self._builder.construir_perfil_saude(perfil)
        self._builder.construir_medicamentos(medicamentos or [])
        self._builder.construir_vacinas(vacinas or [])
        self._builder.construir_consultas(consultas or [])
        self._builder.construir_documentos(documentos or [])
        self._builder.construir_rodape()
        return self._builder.obter_resultado()
