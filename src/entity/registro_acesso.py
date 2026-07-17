from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class RegistroAcesso:
    """Evento de acesso de um usuário ao sistema.

    Guarda uma cópia dos dados de identificação do usuário (login e tipo) no
    momento do acesso, para que os relatórios de estatísticas possam ser
    gerados sem depender do estado atual da coleção de usuários.
    """

    usuario_id: str
    login: str
    tipo_usuario: str
    acao: str = "LOGIN"
    momento: datetime = field(default_factory=datetime.now)
