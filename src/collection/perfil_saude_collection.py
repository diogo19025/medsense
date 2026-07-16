from entity.perfil_saude import PerfilSaude


class PerfilSaudeCollection:
    """Coleção em memória de perfis de saúde.

    Armazena no máximo um perfil por usuário (composição 1:1 com
    FamiliarPaciente no diagrama de classes), servindo de cache de
    trabalho para as operações de CRUD da camada de controle.
    """

    def __init__(self):
        self._perfis: list[PerfilSaude] = []

    # Adiciona um novo perfil à coleção.
    # Lança ValueError se o usuário já possui um perfil de saúde.
    def adicionar(self, perfil: PerfilSaude) -> None:
        if self.buscar_por_usuario(perfil.usuario_id) is not None:
            raise ValueError(
                f"O usuário '{perfil.usuario_id}' já possui um perfil de saúde."
            )
        self._perfis.append(perfil)

    # Substitui o perfil existente do mesmo usuário, preservando a ordem.
    # Lança ValueError se o usuário ainda não possui perfil.
    def atualizar(self, perfil: PerfilSaude) -> None:
        atual = self.buscar_por_usuario(perfil.usuario_id)
        if atual is None:
            raise ValueError(
                f"O usuário '{perfil.usuario_id}' não possui um perfil de saúde."
            )
        self._perfis[self._perfis.index(atual)] = perfil

    # Remove um perfil da coleção pelo id (no-op se não encontrado).
    def remover(self, perfil: PerfilSaude) -> None:
        self._perfis = [p for p in self._perfis if p.id != perfil.id]

    # Retorna uma cópia da lista com todos os perfis cadastrados.
    def listar_todos(self) -> list[PerfilSaude]:
        return list(self._perfis)

    # Busca o perfil de um usuário. Retorna None se não encontrado.
    def buscar_por_usuario(self, usuario_id: str) -> PerfilSaude | None:
        for perfil in self._perfis:
            if perfil.usuario_id == usuario_id:
                return perfil
        return None

    # Retorna a quantidade total de perfis na coleção.
    def quantidade(self) -> int:
        return len(self._perfis)
