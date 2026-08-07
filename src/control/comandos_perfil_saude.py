from control.comando import Comando
from control.historico_perfil_saude import HistoricoPerfilSaude
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
    """Salva o estado anterior e delega a atualização ao receiver."""

    def __init__(
        self,
        receiver: PerfilSaudeControl,
        historico: HistoricoPerfilSaude,
        email: str,
        dados: dict,
    ):
        self._receiver = receiver
        self._historico = historico
        self._email = email
        self._dados = dados

    def executar(self) -> PerfilSaude:
        perfil = self._receiver.buscar_perfil(self._email)
        if perfil is None:
            raise ValueError(
                f"O usuario '{self._email}' nao possui perfil de saude."
            )
        estado_anterior = perfil.criar_memento()
        atualizado = self._receiver.atualizar_perfil(self._email, self._dados)
        self._historico.salvar(estado_anterior)
        return atualizado


class RemoverPerfilSaudeCommand(Comando):
    """Encapsula a remoção, delega ao receiver e descarta o retrato."""

    def __init__(
        self,
        receiver: PerfilSaudeControl,
        historico: HistoricoPerfilSaude,
        email: str,
    ):
        self._receiver = receiver
        self._historico = historico
        self._email = email

    def executar(self) -> None:
        self._receiver.remover_perfil(self._email)
        # Sem o Originator não há o que restaurar. Manter o retrato deixaria
        # o desfazer preso num erro permanente, inclusive depois de o
        # paciente cadastrar um perfil novo.
        self._historico.limpar()
