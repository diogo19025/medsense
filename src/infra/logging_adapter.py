import logging

from infra.logger import Logger

FORMATO_PADRAO = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class LoggingAdapter(Logger):
    """Adapter entre a porta `Logger` e o módulo `logging` da biblioteca padrão.

    Papéis do padrão Adapter neste cenário:
      - Target  : `Logger` (contrato de domínio: info/aviso/erro);
      - Adaptee : `logging.Logger` (API da stdlib: info/warning/error);
      - Adapter : esta classe, que traduz as chamadas de domínio para o Adaptee.

    Trocar de biblioteca de log (loguru, structlog, etc.) passa a ser questão
    de escrever um novo adapter, sem tocar na camada de negócio.
    """

    def __init__(
        self,
        nome: str = "medsense",
        nivel: int = logging.INFO,
        formato: str = FORMATO_PADRAO,
    ):
        self._logger = logging.getLogger(nome)
        self._logger.setLevel(nivel)
        # Configura um handler de console apenas uma vez por logger nomeado,
        # evitando mensagens duplicadas se o adapter for instanciado de novo.
        if not self._logger.handlers:
            manipulador = logging.StreamHandler()
            manipulador.setFormatter(logging.Formatter(formato))
            self._logger.addHandler(manipulador)

    # Traduz info de domínio para logging.info (Adaptee).
    def info(self, mensagem: str) -> None:
        self._logger.info(mensagem)

    # Traduz aviso de domínio para logging.warning (Adaptee).
    def aviso(self, mensagem: str) -> None:
        self._logger.warning(mensagem)

    # Traduz erro de domínio para logging.error (Adaptee).
    def erro(self, mensagem: str) -> None:
        self._logger.error(mensagem)
