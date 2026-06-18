import pickle
from pathlib import Path

from collection.repositorio_usuario import RepositorioUsuario
from entity.exceptions import ArquivoPersistenciaError
from entity.usuario import Usuario

ARQUIVO_PADRAO = "usuarios.dat"


class RepositorioArquivoBinario(RepositorioUsuario):
    """Persistência de usuários em arquivo binário (pickle).

    Toda operação de I/O é envolvida em tratamento de exceções: falhas de
    sistema de arquivos (OSError, análogo a IOException) ou de serialização
    são convertidas em ArquivoPersistenciaError para a camada de aplicação.
    """

    def __init__(self, caminho: str = ARQUIVO_PADRAO):
        self._caminho = Path(caminho)

    # Lê os usuários do arquivo; retorna lista vazia se ele ainda não existe.
    def carregar(self) -> list[Usuario]:
        if not self._caminho.exists():
            return []
        try:
            with open(self._caminho, "rb") as arquivo:
                return pickle.load(arquivo)
        except (OSError, pickle.PickleError, EOFError) as erro:
            raise ArquivoPersistenciaError(
                f"Falha ao ler o arquivo de usuários '{self._caminho}': {erro}"
            ) from erro

    # Grava toda a coleção de usuários no arquivo binário.
    def salvar(self, usuarios: list[Usuario]) -> None:
        try:
            with open(self._caminho, "wb") as arquivo:
                pickle.dump(usuarios, arquivo)
        except (OSError, pickle.PickleError) as erro:
            raise ArquivoPersistenciaError(
                f"Falha ao gravar o arquivo de usuários '{self._caminho}': {erro}"
            ) from erro
