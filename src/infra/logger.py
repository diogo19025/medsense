from abc import ABC, abstractmethod


class Logger(ABC):
    """Porta de log (Target do padrão Adapter).

    Contrato de domínio que a camada de negócio conhece. A camada de
    controle depende apenas desta abstração, e não de nenhuma biblioteca
    concreta de log. As implementações (adapters) traduzem este contrato
    para a API da biblioteca escolhida — ver `LoggingAdapter`.
    """

    # Registra um evento informativo do sistema.
    @abstractmethod
    def info(self, mensagem: str) -> None: ...

    # Registra uma situação de atenção que não interrompe o fluxo.
    @abstractmethod
    def aviso(self, mensagem: str) -> None: ...

    # Registra uma falha ocorrida durante uma operação.
    @abstractmethod
    def erro(self, mensagem: str) -> None: ...


class LoggerNulo(Logger):
    """Implementação nula (Null Object) da porta de log.

    Usada como padrão quando nenhum logger é injetado, permitindo que a
    camada de negócio sempre chame o logger sem checagens de `None` e sem
    poluir a saída (útil em testes).
    """

    def info(self, mensagem: str) -> None:
        pass

    def aviso(self, mensagem: str) -> None:
        pass

    def erro(self, mensagem: str) -> None:
        pass
