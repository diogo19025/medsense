from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from entity.validador_lembrete_saude import ValidadorLembreteSaude

class TipoLembrete(Enum):
    MEDICAMENTO = "medicamento"
    CONSULTA = "consulta"
    EXAME = "exame"
    OUTRO = "outro"

class SituacaoLembrete(Enum):
    PENDENTE = "pendente"
    CONCLUIDO = "concluído"
    CANCELADO = "cancelado"

@dataclass
class LembreteSaude:
    id_lembrete: str
    usuario_id: str
    titulo: str
    descricao: str
    data_hora: datetime
    tipo: TipoLembrete
    situacao: SituacaoLembrete = SituacaoLembrete.PENDENTE

    # Valida e normaliza os campos assim que o lembrete é construído.
    def __post_init__(self) -> None:
        ValidadorLembreteSaude.validar_identificador(self.id_lembrete)
        ValidadorLembreteSaude.validar_usuario_id(self.usuario_id)
        ValidadorLembreteSaude.validar_titulo(self.titulo)
        ValidadorLembreteSaude.validar_data_hora(self.data_hora)
        ValidadorLembreteSaude.validar_opcao(self.tipo, TipoLembrete, "tipo")
        ValidadorLembreteSaude.validar_opcao(
            self.situacao, SituacaoLembrete, "situacao"
        )
        self.titulo = self.titulo.strip()

    def concluir(self) -> None:
        """marca o lembrete como concluído"""
        self.situacao = SituacaoLembrete.CONCLUIDO

    def cancelar(self) -> None:
        """marca o lembrete como cancelado"""
        self.situacao = SituacaoLembrete.CANCELADO
