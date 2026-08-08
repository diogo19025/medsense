import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from control.lembrete_control import LembreteControl
from control.observadores_lembrete import ObservadorLembrete
from control.usuario_control import UsuarioControl
from entity.lembrete_saude import LembreteSaude, SituacaoLembrete, TipoLembrete
from infra.logger import Logger


# ESPIÃO PARA TESTAR O OBSERVER

class ObservadorEspiao(ObservadorLembrete):
    """Duplo de teste que captura as notificações disparadas pelo Subject."""

    def __init__(self):
        self.notificacoes: list[tuple[LembreteSaude, str]] = []

    def notificar(self, lembrete: LembreteSaude, acao: str) -> None:
        self.notificacoes.append((lembrete, acao))


class ObservadorQuebrado(ObservadorLembrete):
    """Duplo de teste que simula um observador com defeito."""

    def notificar(self, lembrete: LembreteSaude, acao: str) -> None:
        raise RuntimeError("observador indisponivel")


class LoggerEspiao(Logger):
    """Duplo de teste que captura as mensagens registradas pelo Subject."""

    def __init__(self):
        self.erros: list[str] = []

    def info(self, mensagem: str) -> None:
        pass

    def aviso(self, mensagem: str) -> None:
        pass

    def erro(self, mensagem: str) -> None:
        self.erros.append(mensagem)


# HELPERS DE DADOS

EMAIL_PACIENTE = "ana@email.com"

def _usuario_control():
    """Cria uma controladora de usuários com uma paciente já cadastrada."""
    usuarios = UsuarioControl()
    usuarios.adicionar_familiar_paciente({
        "nome": "Ana Silva",
        "login": "ana",
        "email": EMAIL_PACIENTE,
        "senha": "SenhaForte1",
        "data_nascimento": "2000-01-01",
        "parentesco": "Filha",
    })
    return usuarios

def _dados_lembrete(id_lembrete="L1"):
    return {
        "id_lembrete": id_lembrete,
        "titulo": "Tomar Losartana",
        "descricao": "1 comprimido de 50mg",
        "data_hora": datetime(2026, 8, 10, 8, 0),
        "tipo": TipoLembrete.MEDICAMENTO
    }


# SUÍTE DE TESTES

class LembreteControlObserverTest(unittest.TestCase):
    def setUp(self):
        self._usuarios = _usuario_control()
        self._control = LembreteControl(self._usuarios)
        self._espiao = ObservadorEspiao()

    def test_deve_anexar_e_notificar_observador_na_criacao(self):
        self._control.anexar_observador(self._espiao)
        
        lembrete = self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())
        
        self.assertEqual(len(self._espiao.notificacoes), 1)
        notificado, acao = self._espiao.notificacoes[0]
        self.assertIs(notificado, lembrete)
        self.assertEqual(acao, "criado")

    def test_deve_notificar_observador_na_atualizacao(self):
        self._control.anexar_observador(self._espiao)
        self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())
        self._espiao.notificacoes.clear() # Limpa notificação de criação
        
        novo = self._control.atualizar_lembrete("L1", {"titulo": "Tomar Losartana 100mg"})
        
        self.assertEqual(len(self._espiao.notificacoes), 1)
        notificado, acao = self._espiao.notificacoes[0]
        self.assertEqual(notificado.titulo, "Tomar Losartana 100mg")
        self.assertEqual(acao, "atualizado")

    def test_deve_notificar_observador_na_conclusao(self):
        self._control.anexar_observador(self._espiao)
        self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())
        self._espiao.notificacoes.clear()
        
        self._control.concluir_lembrete("L1")
        
        self.assertEqual(len(self._espiao.notificacoes), 1)
        notificado, acao = self._espiao.notificacoes[0]
        self.assertEqual(acao, "concluído")
        self.assertEqual(notificado.situacao, SituacaoLembrete.CONCLUIDO)

    def test_deve_notificar_observador_no_cancelamento(self):
        self._control.anexar_observador(self._espiao)
        self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())
        self._espiao.notificacoes.clear()

        self._control.cancelar_lembrete("L1")

        notificado, acao = self._espiao.notificacoes[0]
        self.assertEqual(acao, "cancelado")
        self.assertEqual(notificado.situacao, SituacaoLembrete.CANCELADO)

    def test_deve_notificar_observador_na_remocao(self):
        self._control.anexar_observador(self._espiao)
        self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())
        self._espiao.notificacoes.clear()

        self._control.remover_lembrete("L1")

        _, acao = self._espiao.notificacoes[0]
        self.assertEqual(acao, "removido")
        self.assertEqual(self._control.listar_lembretes(), [])

    def test_deve_lancar_erro_ao_cancelar_lembrete_inexistente(self):
        with self.assertRaisesRegex(ValueError, "nao foi encontrado|não foi encontrado"):
            self._control.cancelar_lembrete("inexistente")

    def test_deve_lancar_erro_ao_remover_lembrete_inexistente(self):
        with self.assertRaisesRegex(ValueError, "nao foi encontrado|não foi encontrado"):
            self._control.remover_lembrete("inexistente")

    def test_nao_deve_notificar_observador_desanexado(self):
        self._control.anexar_observador(self._espiao)
        self._control.desanexar_observador(self._espiao)
        
        self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())
        
        self.assertEqual(len(self._espiao.notificacoes), 0)

    def test_deve_lancar_erro_ao_criar_lembrete_para_email_inexistente(self):
        with self.assertRaises(ValueError):
            self._control.criar_lembrete("nao@existe.com", _dados_lembrete())

    def test_falha_de_observador_nao_deve_interromper_a_operacao(self):
        self._control.anexar_observador(ObservadorQuebrado())

        lembrete = self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())

        self.assertEqual(self._control.listar_lembretes(), [lembrete])

    def test_falha_de_observador_nao_deve_impedir_a_notificacao_dos_demais(self):
        self._control.anexar_observador(ObservadorQuebrado())
        self._control.anexar_observador(self._espiao)

        self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())

        self.assertEqual(len(self._espiao.notificacoes), 1)

    def test_falha_de_observador_deve_ser_registrada_no_log(self):
        logger = LoggerEspiao()
        control = LembreteControl(self._usuarios, logger=logger)
        control.anexar_observador(ObservadorQuebrado())

        control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())

        (erro,) = logger.erros
        self.assertIn("ObservadorQuebrado", erro)
        self.assertIn("observador indisponivel", erro)

if __name__ == "__main__":
    unittest.main()
