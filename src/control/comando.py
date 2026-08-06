from abc import ABC, abstractmethod
from typing import Any


class Comando(ABC):
    """Contrato dos comandos executados pela camada de controle."""

    @abstractmethod
    def executar(self) -> Any: ...
