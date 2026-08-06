from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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
    
    def concluir(self) -> None:
        """marca o lembrete como concluído"""
        self.situacao = SituacaoLembrete.CONCLUIDO

    def cancelar(self) -> None:
        """marca o lembrete como cancelado"""
        self.situacao = SituacaoLembrete.CANCELADO
        