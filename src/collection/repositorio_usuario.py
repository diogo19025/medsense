from abc import ABC, abstractmethod

from entity.usuario import Usuario


class RepositorioUsuario(ABC):
    """Contrato de persistência de usuários (padrão Repository).

    A interface vive na camada de negócio e as implementações concretas na
    infraestrutura (infra/persistencia) — Inversão de Dependência: a camada
    de negócio define o contrato e nunca importa código de infra. O
    mecanismo de armazenamento (memória, arquivo binário ou banco de dados)
    é selecionado pela FabricaRepositorios no início da execução
    ("chaveamento").
    """

    # Lê todos os usuários do meio durável. Lança PersistenciaError em falha.
    @abstractmethod
    def carregar(self) -> list[Usuario]: ...

    # Grava a coleção completa de usuários. Lança PersistenciaError em falha.
    @abstractmethod
    def salvar(self, usuarios: list[Usuario]) -> None: ...
