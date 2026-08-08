from datetime import datetime
from enum import Enum

from entity.exceptions import LembreteSaudeInvalidoError


class ValidadorLembreteSaude:
    """Valida os campos de cadastro de um lembrete de saúde.

    Segue o mesmo desenho de `ValidadorPerfilSaude`: a entidade chama o
    validador na construção e o domínio nunca chega a existir num estado
    inválido. As enumerações de tipo e situação são informadas pelo
    próprio `LembreteSaude`, que é quem as declara.
    """

    # Valida o identificador do lembrete, usado como chave na coleção.
    @staticmethod
    def validar_identificador(id_lembrete: object) -> None:
        ValidadorLembreteSaude._exigir_texto(
            id_lembrete, "O lembrete deve ter um identificador."
        )

    # Valida o vínculo obrigatório com o usuário dono do lembrete.
    @staticmethod
    def validar_usuario_id(usuario_id: object) -> None:
        ValidadorLembreteSaude._exigir_texto(
            usuario_id, "O lembrete deve estar vinculado a um usuário."
        )

    # Valida o título exibido nas listagens e nas notificações.
    @staticmethod
    def validar_titulo(titulo: object) -> None:
        ValidadorLembreteSaude._exigir_texto(
            titulo, "O lembrete deve ter um título."
        )

    # Valida a data e hora, que os observadores formatam como datetime.
    @staticmethod
    def validar_data_hora(data_hora: object) -> None:
        if not isinstance(data_hora, datetime):
            raise LembreteSaudeInvalidoError(
                "A data e hora do lembrete deve ser um datetime."
            )

    # Valida que o valor pertence à enumeração de opções do campo.
    @staticmethod
    def validar_opcao(valor: object, opcoes: type[Enum], campo: str) -> None:
        if not isinstance(valor, opcoes):
            validas = ", ".join(opcao.value for opcao in opcoes)
            raise LembreteSaudeInvalidoError(
                f"Valor inválido para {campo}: '{valor}'. Válidos: {validas}."
            )

    @staticmethod
    def _exigir_texto(valor: object, mensagem: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise LembreteSaudeInvalidoError(mensagem)
