from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ResumoSaude:
    """Resumo de saúde de um paciente, já montado (Product do padrão Builder).

    Reúne num único documento os dados de identificação do usuário e as
    informações clínicas do seu perfil de saúde. É o **resultado final da
    construção**: nasce pronto das mãos de um `ResumoSaudeBuilder` e não
    muda depois (dataclass congelada), no mesmo espírito de
    `RegistroAcesso`.

    `conteudo` guarda o documento já formatado no `formato` do builder que
    o construiu, e `secoes` registra, na ordem de montagem, o nome das
    seções efetivamente incluídas — as opcionais (medicamentos, vacinas,
    consultas e documentos) só aparecem quando há dados para elas.
    """

    usuario_id: str
    formato: str
    conteudo: str
    secoes: tuple[str, ...] = ()
    gerado_em: datetime = field(default_factory=datetime.now)

    # Formata os dados principais do resumo.
    def __str__(self) -> str:
        return (
            f"[{self.usuario_id[:8]}...] Resumo de saude ({self.formato})"
            f" | Secoes: {len(self.secoes)}"
            f" | Gerado em: {self.gerado_em.strftime('%d/%m/%Y %H:%M:%S')}"
        )
