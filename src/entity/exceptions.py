class ValidacaoError(Exception):
    """Erro base para falhas de validação de dados de usuário."""


class LoginInvalidoError(ValidacaoError):
    """Login informado viola as regras de cadastro."""


class SenhaInvalidaError(ValidacaoError):
    """Senha informada viola a política de segurança."""
