from entity.exceptions import PerfilSaudeInvalidoError

TIPOS_SANGUINEOS_VALIDOS = frozenset(
    {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
)


class ValidadorPerfilSaude:
    """Valida os campos de cadastro de um perfil de saúde.

    Os tipos sanguíneos aceitos seguem a classificação ABO/Rh.
    """

    # Valida o vínculo obrigatório com o usuário dono do perfil.
    @staticmethod
    def validar_usuario_id(usuario_id: str) -> None:
        if not usuario_id.strip():
            raise PerfilSaudeInvalidoError(
                "O perfil de saúde deve estar vinculado a um usuário."
            )

    # Valida o tipo sanguíneo contra a classificação ABO/Rh.
    @staticmethod
    def validar_tipo_sanguineo(tipo_sanguineo: str) -> None:
        if tipo_sanguineo not in TIPOS_SANGUINEOS_VALIDOS:
            validos = ", ".join(sorted(TIPOS_SANGUINEOS_VALIDOS))
            raise PerfilSaudeInvalidoError(
                f"Tipo sanguíneo inválido: '{tipo_sanguineo}'. "
                f"Válidos: {validos}."
            )
