from abc import ABC, abstractmethod

from entity.registro_acesso import RegistroAcesso


class RepositorioAcesso(ABC):
    """Contrato de persistência de registros de acesso (padrão Repository).

    Mesmo papel do RepositorioUsuario, aplicado à entidade RegistroAcesso:
    a interface vive na camada de negócio e as implementações concretas na
    infraestrutura, de modo que o negócio registre e consulte acessos sem
    conhecer o mecanismo de armazenamento escolhido no início da execução.
    """

    # Lê todos os registros de acesso. Lança PersistenciaError em falha.
    @abstractmethod
    def carregar(self) -> list[RegistroAcesso]: ...

    # Grava a coleção completa de registros. Lança PersistenciaError em falha.
    @abstractmethod
    def salvar(self, registros: list[RegistroAcesso]) -> None: ...
