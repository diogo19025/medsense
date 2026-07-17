from collection.repositorio_acesso import RepositorioAcesso
from collection.repositorio_perfil_saude import RepositorioPerfilSaude
from collection.repositorio_usuario import RepositorioUsuario
from entity.perfil_saude import PerfilSaude
from entity.registro_acesso import RegistroAcesso
from entity.usuario import Usuario


class RepositorioUsuarioMemoria(RepositorioUsuario):
    """Persistência de usuários em memória RAM.

    Guarda a coleção apenas durante a execução do processo (mesmo espírito
    do LoggerNulo): permite que a camada de negócio trate o mecanismo em
    RAM pelo mesmo contrato dos mecanismos duráveis, sem checagens de tipo.
    """

    def __init__(self):
        self._usuarios: list[Usuario] = []

    def carregar(self) -> list[Usuario]:
        return list(self._usuarios)

    def salvar(self, usuarios: list[Usuario]) -> None:
        self._usuarios = list(usuarios)


class RepositorioAcessoMemoria(RepositorioAcesso):
    """Persistência de registros de acesso em memória RAM."""

    def __init__(self):
        self._registros: list[RegistroAcesso] = []

    def carregar(self) -> list[RegistroAcesso]:
        return list(self._registros)

    def salvar(self, registros: list[RegistroAcesso]) -> None:
        self._registros = list(registros)


class RepositorioPerfilSaudeMemoria(RepositorioPerfilSaude):
    """Persistência de perfis de saúde em memória RAM."""

    def __init__(self):
        self._perfis: list[PerfilSaude] = []

    def carregar(self) -> list[PerfilSaude]:
        return list(self._perfis)

    def salvar(self, perfis: list[PerfilSaude]) -> None:
        self._perfis = list(perfis)
