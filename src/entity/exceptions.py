class ValidacaoError(Exception):
    """Erro base para falhas de validação de dados de usuário."""


class LoginInvalidoError(ValidacaoError):
    """Login informado viola as regras de cadastro."""


class SenhaInvalidaError(ValidacaoError):
    """Senha informada viola a política de segurança."""


class PerfilSaudeInvalidoError(ValidacaoError):
    """Perfil de saúde informado viola as regras de cadastro."""


class LembreteSaudeInvalidoError(ValidacaoError):
    """Lembrete de saúde informado viola as regras de cadastro."""


class PersistenciaError(Exception):
    """Erro base para falhas ao persistir ou recuperar usuários."""


class ArquivoPersistenciaError(PersistenciaError):
    """Falha de I/O no arquivo binário de usuários (análogo a IOException)."""


class BancoDadosError(PersistenciaError):
    """Falha ao acessar o banco de dados de usuários (análogo a SQLException)."""
