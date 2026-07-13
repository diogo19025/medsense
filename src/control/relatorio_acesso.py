from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from html import escape

from entity.registro_acesso import RegistroAcesso


@dataclass(frozen=True)
class EstatisticasAcesso:
    """Estatísticas de acesso agregadas, consumidas pelos relatórios."""

    total_acessos: int
    usuarios_distintos: int
    acessos_por_login: dict[str, int]
    acessos_por_tipo: dict[str, int]
    primeiro_acesso: datetime | None
    ultimo_acesso: datetime | None
    usuario_mais_ativo: str | None


class RelatorioAcesso(ABC):
    """Gerador de relatório de estatísticas de acesso (Template Method).

    `gerar()` é o **template method**: fixa o esqueleto invariante do
    algoritmo (calcular estatísticas → montar seções na ordem definida). As
    subclasses não reescrevem esse fluxo; implementam apenas as *primitive
    operations* de formatação (`_cabecalho`, `_secao_resumo`,
    `_secao_por_usuario`, `_rodape`, `_montar`), cada uma específica de um
    formato de saída (HTML, texto, e futuramente PDF).
    """

    def __init__(self, registros: list[RegistroAcesso]):
        self._registros = registros

    # -------- Template method (invariante — não sobrescrever) --------
    def gerar(self) -> str:
        estatisticas = self._calcular_estatisticas()
        partes = [
            self._cabecalho(estatisticas),
            self._secao_resumo(estatisticas),
            self._secao_por_usuario(estatisticas),
            self._rodape(estatisticas),
        ]
        return self._montar(partes)

    # -------- Passo concreto comum a todos os formatos --------
    # Agrega os registros em estatísticas. É a única regra de negócio do
    # relatório e, por ser idêntica em todos os formatos, vive na base.
    def _calcular_estatisticas(self) -> EstatisticasAcesso:
        por_login = Counter(registro.login for registro in self._registros)
        por_tipo = Counter(registro.tipo_usuario for registro in self._registros)
        momentos = [registro.momento for registro in self._registros]
        mais_ativo = por_login.most_common(1)[0][0] if por_login else None

        return EstatisticasAcesso(
            total_acessos=len(self._registros),
            usuarios_distintos=len(por_login),
            acessos_por_login=dict(por_login),
            acessos_por_tipo=dict(por_tipo),
            primeiro_acesso=min(momentos) if momentos else None,
            ultimo_acesso=max(momentos) if momentos else None,
            usuario_mais_ativo=mais_ativo,
        )

    # -------- Primitive operations (formato-específicas) --------
    @property
    @abstractmethod
    # Extensão de arquivo sugerida para o formato (ex.: "html", "txt").
    def extensao(self) -> str: ...

    @abstractmethod
    # Cabeçalho/título do relatório.
    def _cabecalho(self, estatisticas: EstatisticasAcesso) -> str: ...

    @abstractmethod
    # Seção com os números gerais de acesso.
    def _secao_resumo(self, estatisticas: EstatisticasAcesso) -> str: ...

    @abstractmethod
    # Seção detalhando os acessos por usuário e por tipo.
    def _secao_por_usuario(self, estatisticas: EstatisticasAcesso) -> str: ...

    @abstractmethod
    # Rodapé do relatório (ex.: data de geração).
    def _rodape(self, estatisticas: EstatisticasAcesso) -> str: ...

    @abstractmethod
    # Junta as seções no documento final do formato.
    def _montar(self, partes: list[str]) -> str: ...

    # -------- Utilitário comum de formatação --------
    @staticmethod
    def _formatar_data(momento: datetime | None) -> str:
        return momento.strftime("%d/%m/%Y %H:%M:%S") if momento else "-"


class RelatorioAcessoTexto(RelatorioAcesso):
    """Relatório de acessos em texto puro (adequado a console/arquivo .txt)."""

    @property
    def extensao(self) -> str:
        return "txt"

    def _cabecalho(self, estatisticas: EstatisticasAcesso) -> str:
        titulo = "MedSense - Relatorio de Acessos"
        return f"{titulo}\n{'=' * len(titulo)}"

    def _secao_resumo(self, estatisticas: EstatisticasAcesso) -> str:
        return (
            "Resumo\n"
            f"  Total de acessos.....: {estatisticas.total_acessos}\n"
            f"  Usuarios distintos...: {estatisticas.usuarios_distintos}\n"
            f"  Primeiro acesso......: {self._formatar_data(estatisticas.primeiro_acesso)}\n"
            f"  Ultimo acesso........: {self._formatar_data(estatisticas.ultimo_acesso)}\n"
            f"  Usuario mais ativo...: {estatisticas.usuario_mais_ativo or '-'}"
        )

    def _secao_por_usuario(self, estatisticas: EstatisticasAcesso) -> str:
        linhas = ["Acessos por usuario"]
        for login, total in sorted(
            estatisticas.acessos_por_login.items(), key=lambda item: (-item[1], item[0])
        ):
            linhas.append(f"  {login}: {total}")

        linhas.append("Acessos por tipo de usuario")
        for tipo, total in sorted(estatisticas.acessos_por_tipo.items()):
            linhas.append(f"  {tipo}: {total}")
        return "\n".join(linhas)

    def _rodape(self, estatisticas: EstatisticasAcesso) -> str:
        return f"Gerado em {self._formatar_data(datetime.now())}"

    def _montar(self, partes: list[str]) -> str:
        return "\n\n".join(partes) + "\n"


class RelatorioAcessoHTML(RelatorioAcesso):
    """Relatório de acessos em HTML (adequado a navegador/arquivo .html)."""

    @property
    def extensao(self) -> str:
        return "html"

    def _cabecalho(self, estatisticas: EstatisticasAcesso) -> str:
        return "<h1>MedSense &ndash; Relat&oacute;rio de Acessos</h1>"

    def _secao_resumo(self, estatisticas: EstatisticasAcesso) -> str:
        return (
            "<h2>Resumo</h2>\n<ul>\n"
            f"  <li>Total de acessos: <strong>{estatisticas.total_acessos}</strong></li>\n"
            f"  <li>Usu&aacute;rios distintos: <strong>{estatisticas.usuarios_distintos}</strong></li>\n"
            f"  <li>Primeiro acesso: {self._formatar_data(estatisticas.primeiro_acesso)}</li>\n"
            f"  <li>&Uacute;ltimo acesso: {self._formatar_data(estatisticas.ultimo_acesso)}</li>\n"
            f"  <li>Usu&aacute;rio mais ativo: {escape(estatisticas.usuario_mais_ativo or '-')}</li>\n"
            "</ul>"
        )

    def _secao_por_usuario(self, estatisticas: EstatisticasAcesso) -> str:
        linhas = ["<h2>Acessos por usu&aacute;rio</h2>", "<table>", "  <tr><th>Login</th><th>Acessos</th></tr>"]
        for login, total in sorted(
            estatisticas.acessos_por_login.items(), key=lambda item: (-item[1], item[0])
        ):
            linhas.append(f"  <tr><td>{escape(login)}</td><td>{total}</td></tr>")
        linhas.append("</table>")

        linhas.append("<h2>Acessos por tipo de usu&aacute;rio</h2>")
        linhas.append("<table>")
        linhas.append("  <tr><th>Tipo</th><th>Acessos</th></tr>")
        for tipo, total in sorted(estatisticas.acessos_por_tipo.items()):
            linhas.append(f"  <tr><td>{escape(tipo)}</td><td>{total}</td></tr>")
        linhas.append("</table>")
        return "\n".join(linhas)

    def _rodape(self, estatisticas: EstatisticasAcesso) -> str:
        return f"<footer>Gerado em {self._formatar_data(datetime.now())}</footer>"

    def _montar(self, partes: list[str]) -> str:
        corpo = "\n".join(partes)
        return (
            "<!DOCTYPE html>\n"
            '<html lang="pt-br">\n<head>\n'
            '  <meta charset="utf-8">\n'
            "  <title>MedSense - Relatorio de Acessos</title>\n"
            "</head>\n<body>\n"
            f"{corpo}\n"
            "</body>\n</html>\n"
        )


# Mapa de formatos disponíveis -> classe de relatório correspondente.
FORMATOS_DISPONIVEIS: dict[str, type[RelatorioAcesso]] = {
    "texto": RelatorioAcessoTexto,
    "html": RelatorioAcessoHTML,
}


# Seleciona a subclasse de relatório pelo nome do formato.
def criar_relatorio(formato: str, registros: list[RegistroAcesso]) -> RelatorioAcesso:
    try:
        classe = FORMATOS_DISPONIVEIS[formato.lower()]
    except KeyError:
        disponiveis = ", ".join(sorted(FORMATOS_DISPONIVEIS))
        raise ValueError(
            f"Formato de relatorio desconhecido: '{formato}'. Disponiveis: {disponiveis}."
        ) from None
    return classe(registros)
