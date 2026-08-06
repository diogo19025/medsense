import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from control.lembrete_control import LembreteControl
from control.observadores_lembrete import ObservadorLembrete
from control.usuario_control import UsuarioControl
from entity.lembrete_saude import LembreteSaude, TipoLembrete


# ESPIÃO PARA TESTAR O OBSERVER

class ObservadorEspiao(ObservadorLembrete):
    """Duplo de teste que captura as notificações disparadas pelo Subject."""
    
    def __init__(self):
        self.notificacoes: list[tuple[LembreteSaude, str]] = []

    def notificar(self, lembrete: LembreteSaude, acao: str) -> None:
        self.notificacoes.append((lembrete, acao))


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
        self.assertTrue(notificado.situacao) # Verifica se está concluído

    def test_nao_deve_notificar_observador_desanexado(self):
        self._control.anexar_observador(self._espiao)
        self._control.desanexar_observador(self._espiao)
        
        self._control.criar_lembrete(EMAIL_PACIENTE, _dados_lembrete())
        
        self.assertEqual(len(self._espiao.notificacoes), 0)

    def test_deve_lancar_erro_ao_criar_lembrete_para_email_inexistente(self):
        with self.assertRaises(ValueError):
            self._control.criar_lembrete("nao@existe.com", _dados_lembrete())

if __name__ == "__main__":
    unittest.main()