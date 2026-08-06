from entity.perfil_saude_memento import PerfilSaudeMemento


class HistoricoPerfilSaude:
    """Caretaker que mantém somente o estado da última atualização."""

    def __init__(self):
        self._ultimo_estado: PerfilSaudeMemento | None = None

    def salvar(self, memento: PerfilSaudeMemento) -> None:
        self._ultimo_estado = memento

    def recuperar(self) -> PerfilSaudeMemento:
        if self._ultimo_estado is None:
            raise ValueError(
                "Nao existe atualizacao de perfil de saude para desfazer."
            )
        return self._ultimo_estado

    def limpar(self) -> None:
        self._ultimo_estado = None

    def possui_estado(self) -> bool:
        return self._ultimo_estado is not None
