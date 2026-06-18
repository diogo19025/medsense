from abc import ABC, abstractmethod

from entity.usuario import Usuario


class RepositorioUsuario(ABC):
    """Contrato de persistência de usuários.

    Define o ponto de troca ("chaveamento") entre os mecanismos de
    armazenamento. A coleção em RAM (UsuarioCollection) é o cache de
    trabalho; uma implementação deste contrato é o armazenamento durável
    (arquivo binário ou banco de dados) carregado no início da execução.
    """

    # Lê todos os usuários do meio durável. Lança PersistenciaError em falha.
    @abstractmethod
    def carregar(self) -> list[Usuario]: ...

    # Grava a coleção completa de usuários. Lança PersistenciaError em falha.
    @abstractmethod
    def salvar(self, usuarios: list[Usuario]) -> None: ...
