from entity.lembrete_saude import LembreteSaude

class LembreteCollection:
    """Coleção em memória de lembretes de saúde.

    Armazena os lembretes do sistema, servindo de cache de
    trabalho para as operações de CRUD da camada de controle.
    """

    def __init__(self):
        self._lembretes: list[LembreteSaude] = []

    # adiciona um novo lembrete à coleção.
    # lança ValueError se já existir um lembrete com o mesmo id.
    def adicionar(self, lembrete: LembreteSaude) -> None:
        if self.buscar_por_id(lembrete.id_lembrete) is not None:
            raise ValueError(f"Já existe um lembrete com o ID '{lembrete.id_lembrete}'.")
        self._lembretes.append(lembrete)

    # substitui o lembrete existente pelo id, preservando a ordem.
    # lança ValueError se o lembrete não for encontrado.
    def atualizar(self, lembrete: LembreteSaude) -> None:
        atual = self.buscar_por_id(lembrete.id_lembrete)
        if atual is None:
            raise ValueError(f"O lembrete com ID '{lembrete.id_lembrete}' não foi encontrado.")
        self._lembretes[self._lembretes.index(atual)] = lembrete

    # remove um lembrete da coleção pelo id (no-op se não encontrado).
    def remover(self, lembrete: LembreteSaude) -> None:
        self._lembretes = [l for l in self._lembretes if l.id_lembrete != lembrete.id_lembrete]

    # retorna uma cópia da lista com todos os lembretes cadastrados.
    def listar_todos(self) -> list[LembreteSaude]:
        return list(self._lembretes)
    
    # retorna uma lista com os lembretes de um usuário específico.
    def listar_por_usuario(self, usuario_id: str) -> list[LembreteSaude]:
        return [l for l in self._lembretes if l.usuario_id == usuario_id]

    # busca um lembrete pelo id. Retorna None se não encontrado.
    def buscar_por_id(self, id_lembrete: str) -> LembreteSaude | None:
        for lembrete in self._lembretes:
            if lembrete.id_lembrete == id_lembrete:
                return lembrete
        return None

    # retorna a quantidade total de lembretes na coleção.
    def quantidade(self) -> int:
        return len(self._lembretes)
