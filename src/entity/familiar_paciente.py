from dataclasses import dataclass

from entity.usuario import Usuario


@dataclass
class FamiliarPaciente(Usuario):
    data_nascimento: str = ""
    parentesco: str = ""

    # Identifica este usuário como familiar/paciente.
    @property
    def tipo_usuario(self) -> str:
        return "FAMILIAR_PACIENTE"

    # Inclui parentesco e data de nascimento na exibição.
    def __str__(self) -> str:
        return (
            super().__str__()
            + f" | Parentesco: {self.parentesco}"
            + f" | Nascimento: {self.data_nascimento}"
        )