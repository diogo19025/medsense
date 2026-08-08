from abc import ABC, abstractmethod
from entity.lembrete_saude import LembreteSaude
from infra.logger import Logger, LoggerNulo

class ObservadorLembrete(ABC):
    """
    Interface para os observadores de lembretes.
    Qualquer classe que queira reagir a mudanças em lembretes deve implementar esta classe
    """
    
    @abstractmethod
    def notificar(self, lembrete: LembreteSaude, acao: str) -> None:
        """método chamado pelo Subject quando um evento ocorre"""
        pass


class NotificadorConsole(ObservadorLembrete):
    """
    Observador que notifica o usuário via console.
    Simula um alerta visual na tela, como um pop-up ou aviso
    """
    
    def notificar(self, lembrete: LembreteSaude, acao: str) -> None:
        print("\n" + "="*50)
        print(f"NOTIFICAÇÃO: Lembrete {acao.upper()}")
        print(f"Título: {lembrete.titulo} | Tipo: {lembrete.tipo.value}")
        print(f"Data/Hora: {lembrete.data_hora.strftime('%d/%m/%Y %H:%M')}")
        print(f"Situação atual: {lembrete.situacao.value}")
        print("="*50 + "\n")


class RegistroNotificacaoObserver(ObservadorLembrete):
    """
    Observador responsável por auditar/logar os eventos de lembretes
    """
    
    def __init__(self, logger: Logger = None):
        # usa a porta Logger da infraestrutura. 
        # se nenhum for injetado, usa o Null Object (LoggerNulo) para evitar quebras
        self._logger = logger or LoggerNulo()

    def notificar(self, lembrete: LembreteSaude, acao: str) -> None:
        # usa o método info do contrato Logger
        mensagem = (
            f"Evento de Lembrete: Ação '{acao}' executada no lembrete "
            f"ID '{lembrete.id_lembrete}' do usuário '{lembrete.usuario_id}'."
        )
        self._logger.info(mensagem)
