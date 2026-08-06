from typing import Any

from control.comando import Comando


class ExecutorComandos:
    """Invoker responsável por disparar comandos de forma uniforme."""

    def executar(self, comando: Comando) -> Any:
        return comando.executar()
