from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import uuid4

from entity.validador_usuario import ValidadorUsuario


@dataclass
class Usuario(ABC):
    nome: str
    login: str
    email: str
    senha: str
    id: str = field(default_factory=lambda: str(uuid4()))

    # Valida os campos obrigatórios assim que o usuário é construído.
    def __post_init__(self) -> None:
        ValidadorUsuario.validar_login(self.login)
        ValidadorUsuario.validar_senha(self.senha, (self.login, self.nome, self.email))

    @property
    @abstractmethod
    # Retorna o tipo do usuário (implementado pelas subclasses).
    def tipo_usuario(self) -> str: ...

    # Formata os dados principais do usuário.
    def __str__(self) -> str:
        return (
            f"[{self.id[:8]}...] {self.nome} (login: {self.login}) "
            f"| {self.email} | Tipo: {self.tipo_usuario}"
        )