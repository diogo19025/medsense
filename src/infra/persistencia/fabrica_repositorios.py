from abc import ABC, abstractmethod

from infra.persistencia.repositorio_acesso import RepositorioAcesso
from infra.persistencia.repositorio_arquivo import (
    ARQUIVO_ACESSOS_PADRAO,
    ARQUIVO_USUARIOS_PADRAO,
    RepositorioAcessoArquivo,
    RepositorioArquivoBinario,
)
from infra.persistencia.repositorio_memoria import (
    RepositorioAcessoMemoria,
    RepositorioUsuarioMemoria,
)
from infra.persistencia.repositorio_sqlite import (
    BANCO_PADRAO,
    RepositorioAcessoSQLite,
    RepositorioSQLite,
)
from infra.persistencia.repositorio_usuario import RepositorioUsuario


class FabricaRepositorios(ABC):
    """Fábrica abstrata de repositórios (padrão Abstract Factory).

    Cada fábrica concreta produz a família completa de repositórios de um
    mesmo mecanismo de armazenamento (um repositório por entidade). A
    escolha da fábrica no início da execução "chaveia" toda a persistência
    de uma vez, sem que as camadas de negócio conheçam as classes concretas.
    """

    # Cria o repositório de usuários da família.
    @abstractmethod
    def criar_repositorio_usuarios(self) -> RepositorioUsuario: ...

    # Cria o repositório de registros de acesso da família.
    @abstractmethod
    def criar_repositorio_acessos(self) -> RepositorioAcesso: ...


class FabricaRepositoriosMemoria(FabricaRepositorios):
    """Família de repositórios em memória RAM (sem durabilidade)."""

    def criar_repositorio_usuarios(self) -> RepositorioUsuario:
        return RepositorioUsuarioMemoria()

    def criar_repositorio_acessos(self) -> RepositorioAcesso:
        return RepositorioAcessoMemoria()


class FabricaRepositoriosArquivo(FabricaRepositorios):
    """Família de repositórios em arquivo binário (um arquivo por entidade)."""

    def __init__(
        self,
        caminho_usuarios: str = ARQUIVO_USUARIOS_PADRAO,
        caminho_acessos: str = ARQUIVO_ACESSOS_PADRAO,
    ):
        self._caminho_usuarios = caminho_usuarios
        self._caminho_acessos = caminho_acessos

    def criar_repositorio_usuarios(self) -> RepositorioUsuario:
        return RepositorioArquivoBinario(self._caminho_usuarios)

    def criar_repositorio_acessos(self) -> RepositorioAcesso:
        return RepositorioAcessoArquivo(self._caminho_acessos)


class FabricaRepositoriosSQLite(FabricaRepositorios):
    """Família de repositórios em SQLite (mesmo banco, uma tabela por entidade)."""

    def __init__(self, caminho_banco: str = BANCO_PADRAO):
        self._caminho_banco = caminho_banco

    def criar_repositorio_usuarios(self) -> RepositorioUsuario:
        return RepositorioSQLite(self._caminho_banco)

    def criar_repositorio_acessos(self) -> RepositorioAcesso:
        return RepositorioAcessoSQLite(self._caminho_banco)


# Mapa de mecanismos disponíveis -> fábrica concreta correspondente.
MECANISMOS_DISPONIVEIS: dict[str, type[FabricaRepositorios]] = {
    "memoria": FabricaRepositoriosMemoria,
    "arquivo": FabricaRepositoriosArquivo,
    "sqlite": FabricaRepositoriosSQLite,
}


# Seleciona a fábrica concreta pelo nome do mecanismo de armazenamento.
def criar_fabrica(mecanismo: str) -> FabricaRepositorios:
    try:
        classe = MECANISMOS_DISPONIVEIS[mecanismo.lower()]
    except KeyError:
        disponiveis = ", ".join(sorted(MECANISMOS_DISPONIVEIS))
        raise ValueError(
            f"Mecanismo de armazenamento desconhecido: '{mecanismo}'. "
            f"Disponiveis: {disponiveis}."
        ) from None
    return classe()
