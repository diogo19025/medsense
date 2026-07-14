from entity.registro_acesso import RegistroAcesso


class AcessoCollection:
    """Coleção em memória de registros de acesso.

    Armazena os eventos de acesso na ordem em que ocorrem, servindo de fonte
    de dados para os relatórios de estatísticas de acesso (ver
    `control.relatorio_acesso`).
    """

    def __init__(self):
        self._registros: list[RegistroAcesso] = []

    # Adiciona um novo registro de acesso à coleção.
    def adicionar(self, registro: RegistroAcesso) -> None:
        self._registros.append(registro)

    # Remove um registro da coleção (no-op se não encontrado).
    def remover(self, registro: RegistroAcesso) -> None:
        self._registros = [r for r in self._registros if r is not registro]

    # Retorna uma cópia da lista com todos os registros de acesso.
    def listar_todos(self) -> list[RegistroAcesso]:
        return list(self._registros)

    # Retorna a quantidade total de acessos registrados.
    def quantidade(self) -> int:
        return len(self._registros)
