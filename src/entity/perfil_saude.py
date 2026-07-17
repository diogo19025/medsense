from dataclasses import dataclass, field
from uuid import uuid4

from entity.validador_perfil_saude import ValidadorPerfilSaude


@dataclass
class PerfilSaude:
    """Perfil de saúde de um familiar paciente.

    Guarda as informações clínicas básicas do paciente (tipo sanguíneo,
    alergias, condições crônicas e medicamentos de uso contínuo),
    vinculadas ao usuário dono do perfil pelo `usuario_id` — cada
    FamiliarPaciente possui no máximo um perfil de saúde.
    """

    usuario_id: str
    tipo_sanguineo: str
    alergias: list[str] = field(default_factory=list)
    condicoes_cronicas: list[str] = field(default_factory=list)
    medicamentos_continuos: list[str] = field(default_factory=list)
    observacoes: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))

    # Normaliza e valida os campos assim que o perfil é construído.
    def __post_init__(self) -> None:
        self.tipo_sanguineo = self.tipo_sanguineo.strip().upper()
        ValidadorPerfilSaude.validar_usuario_id(self.usuario_id)
        ValidadorPerfilSaude.validar_tipo_sanguineo(self.tipo_sanguineo)

    # Exibe "-" no lugar de listas vazias para leitura na CLI.
    @staticmethod
    def _formatar_lista(itens: list[str]) -> str:
        return ", ".join(itens) if itens else "-"

    # Formata os dados principais do perfil.
    def __str__(self) -> str:
        return (
            f"[{self.id[:8]}...] Tipo sanguíneo: {self.tipo_sanguineo}"
            f" | Alergias: {self._formatar_lista(self.alergias)}"
            f" | Condições crônicas: {self._formatar_lista(self.condicoes_cronicas)}"
            f" | Medicamentos contínuos: {self._formatar_lista(self.medicamentos_continuos)}"
            f" | Observações: {self.observacoes or '-'}"
        )
