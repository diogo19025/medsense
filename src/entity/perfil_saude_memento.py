from dataclasses import dataclass


@dataclass(frozen=True)
class PerfilSaudeMemento:
    """Retrato imutável de um PerfilSaude antes de uma atualização."""

    id: str
    usuario_id: str
    tipo_sanguineo: str
    alergias: tuple[str, ...]
    condicoes_cronicas: tuple[str, ...]
    medicamentos_continuos: tuple[str, ...]
    observacoes: str
