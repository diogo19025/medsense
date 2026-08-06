from control.comando import Comando
from control.perfil_saude_control import PerfilSaudeControl
from entity.perfil_saude import PerfilSaude


class CadastrarPerfilSaudeCommand(Comando):
    """Encapsula o cadastro e delega as regras ao receiver."""

    def __init__(self, receiver: PerfilSaudeControl, email: str, dados: dict):
        self._receiver = receiver
        self._email = email
        self._dados = dados

    def executar(self) -> PerfilSaude:
        return self._receiver.cadastrar_perfil(self._email, self._dados)


class AtualizarPerfilSaudeCommand(Comando):
    """Encapsula a atualização e delega as regras ao receiver."""

    def __init__(self, receiver: PerfilSaudeControl, email: str, dados: dict):
        self._receiver = receiver
        self._email = email
        self._dados = dados

    def executar(self) -> PerfilSaude:
        return self._receiver.atualizar_perfil(self._email, self._dados)


class RemoverPerfilSaudeCommand(Comando):
    """Encapsula a remoção e delega as regras ao receiver."""

    def __init__(self, receiver: PerfilSaudeControl, email: str):
        self._receiver = receiver
        self._email = email

    def executar(self) -> None:
        self._receiver.remover_perfil(self._email)
