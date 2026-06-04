from dataclasses import dataclass

from entity.usuario import Usuario


@dataclass
class ResponsavelFamiliar(Usuario):
    parentesco_principal: str = ""

    # Identifica este usuário como responsável familiar.
    @property
    def tipo_usuario(self) -> str:
        return "RESPONSAVEL_FAMILIAR"

    # Inclui o parentesco principal na exibição.
    def __str__(self) -> str:
        return super().__str__() + f" | Parentesco principal: {self.parentesco_principal}"