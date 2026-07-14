from abc import ABC, abstractmethod

from entity.usuario import Usuario


class RepositorioUsuario(ABC):
    """Contrato de persistência de usuários (padrão Repository).

    Separa a camada de negócio (control) da camada de persistência (infra):
    o control depende apenas deste contrato, e cada mecanismo de
    armazenamento (memória, arquivo binário ou banco de dados) é uma
    implementação concreta selecionada pela FabricaRepositorios no início
    da execução ("chaveamento").
    """

    # Lê todos os usuários do meio durável. Lança PersistenciaError em falha.
    @abstractmethod
    def carregar(self) -> list[Usuario]: ...

    # Grava a coleção completa de usuários. Lança PersistenciaError em falha.
    @abstractmethod
    def salvar(self, usuarios: list[Usuario]) -> None: ...
