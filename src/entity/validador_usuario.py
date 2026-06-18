from entity.exceptions import LoginInvalidoError, SenhaInvalidaError

LOGIN_TAMANHO_MAXIMO = 12

SENHA_TAMANHO_MINIMO = 8
SENHA_TAMANHO_MAXIMO = 128
SENHA_TIPOS_MINIMOS = 3
SENHA_SIMBOLOS = "!@#$%^&*()_+-=[]{}|'"


class ValidadorUsuario:
    """Valida os campos de cadastro de um usuário.

    As regras de senha seguem a política padrão do AWS IAM:
    https://docs.aws.amazon.com/pt_br/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html
    """

    # Valida o login: obrigatório, curto e sem números.
    @staticmethod
    def validar_login(login: str) -> None:
        if not login.strip():
            raise LoginInvalidoError("O login não pode ser vazio.")
        if len(login) > LOGIN_TAMANHO_MAXIMO:
            raise LoginInvalidoError(
                f"O login deve ter no máximo {LOGIN_TAMANHO_MAXIMO} caracteres."
            )
        if any(caractere.isdigit() for caractere in login):
            raise LoginInvalidoError("O login não pode conter números.")

    # Valida a senha conforme a política padrão do AWS IAM.
    @staticmethod
    def validar_senha(senha: str, identificadores: tuple[str, ...]) -> None:
        if not SENHA_TAMANHO_MINIMO <= len(senha) <= SENHA_TAMANHO_MAXIMO:
            raise SenhaInvalidaError(
                f"A senha deve ter entre {SENHA_TAMANHO_MINIMO} e "
                f"{SENHA_TAMANHO_MAXIMO} caracteres."
            )
        if ValidadorUsuario._contar_tipos_de_caractere(senha) < SENHA_TIPOS_MINIMOS:
            raise SenhaInvalidaError(
                f"A senha deve combinar ao menos {SENHA_TIPOS_MINIMOS} tipos entre "
                "maiúsculas, minúsculas, números e símbolos."
            )
        if senha in identificadores:
            raise SenhaInvalidaError(
                "A senha não pode ser idêntica ao login, nome ou email."
            )

    # Conta quantos dos quatro tipos de caractere aparecem na senha.
    @staticmethod
    def _contar_tipos_de_caractere(senha: str) -> int:
        tem_maiuscula = any(caractere.isupper() for caractere in senha)
        tem_minuscula = any(caractere.islower() for caractere in senha)
        tem_numero = any(caractere.isdigit() for caractere in senha)
        tem_simbolo = any(caractere in SENHA_SIMBOLOS for caractere in senha)
        return sum([tem_maiuscula, tem_minuscula, tem_numero, tem_simbolo])
