import pickle
from pathlib import Path

from collection.repositorio_acesso import RepositorioAcesso
from collection.repositorio_usuario import RepositorioUsuario
from entity.exceptions import ArquivoPersistenciaError
from entity.registro_acesso import RegistroAcesso
from entity.usuario import Usuario

ARQUIVO_USUARIOS_PADRAO = "usuarios.dat"
ARQUIVO_ACESSOS_PADRAO = "acessos.dat"


# Lê uma lista de objetos do arquivo; retorna lista vazia se não existe.
def _carregar_arquivo(caminho: Path, descricao: str) -> list:
    if not caminho.exists():
        return []
    try:
        with open(caminho, "rb") as arquivo:
            return pickle.load(arquivo)
    except (OSError, pickle.PickleError, EOFError) as erro:
        raise ArquivoPersistenciaError(
            f"Falha ao ler o arquivo de {descricao} '{caminho}': {erro}"
        ) from erro


# Grava uma lista de objetos no arquivo binário.
def _salvar_arquivo(caminho: Path, itens: list, descricao: str) -> None:
    try:
        with open(caminho, "wb") as arquivo:
            pickle.dump(itens, arquivo)
    except (OSError, pickle.PickleError) as erro:
        raise ArquivoPersistenciaError(
            f"Falha ao gravar o arquivo de {descricao} '{caminho}': {erro}"
        ) from erro


class RepositorioArquivoBinario(RepositorioUsuario):
    """Persistência de usuários em arquivo binário (pickle).

    Toda operação de I/O é envolvida em tratamento de exceções: falhas de
    sistema de arquivos (OSError, análogo a IOException) ou de serialização
    são convertidas em ArquivoPersistenciaError para a camada de aplicação.
    """

    def __init__(self, caminho: str = ARQUIVO_USUARIOS_PADRAO):
        self._caminho = Path(caminho)

    def carregar(self) -> list[Usuario]:
        return _carregar_arquivo(self._caminho, "usuários")

    def salvar(self, usuarios: list[Usuario]) -> None:
        _salvar_arquivo(self._caminho, usuarios, "usuários")


class RepositorioAcessoArquivo(RepositorioAcesso):
    """Persistência de registros de acesso em arquivo binário (pickle)."""

    def __init__(self, caminho: str = ARQUIVO_ACESSOS_PADRAO):
        self._caminho = Path(caminho)

    def carregar(self) -> list[RegistroAcesso]:
        return _carregar_arquivo(self._caminho, "acessos")

    def salvar(self, registros: list[RegistroAcesso]) -> None:
        _salvar_arquivo(self._caminho, registros, "acessos")
