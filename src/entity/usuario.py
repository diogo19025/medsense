from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Usuario(ABC):
    nome: str
    email: str
    senha: str
    id: str = field(default_factory=lambda: str(uuid4()))

    @property
    @abstractmethod
    # Retorna o tipo do usuário (implementado pelas subclasses).
    def tipo_usuario(self) -> str: ...

    # Formata os dados principais do usuário.
    def __str__(self) -> str:
        return f"[{self.id[:8]}...] {self.nome} | {self.email} | Tipo: {self.tipo_usuario}"