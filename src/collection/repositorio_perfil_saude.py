from abc import ABC, abstractmethod

from entity.perfil_saude import PerfilSaude


class RepositorioPerfilSaude(ABC):
    """Contrato de persistência de perfis de saúde (padrão Repository).

    Mesmo papel do RepositorioUsuario, aplicado à entidade PerfilSaude:
    a interface vive na camada de negócio e as implementações concretas na
    infraestrutura (infra/persistencia), de modo que o negócio gerencie os
    perfis sem conhecer o mecanismo de armazenamento escolhido no início
    da execução.
    """

    # Lê todos os perfis de saúde. Lança PersistenciaError em falha.
    @abstractmethod
    def carregar(self) -> list[PerfilSaude]: ...

    # Grava a coleção completa de perfis. Lança PersistenciaError em falha.
    @abstractmethod
    def salvar(self, perfis: list[PerfilSaude]) -> None: ...
