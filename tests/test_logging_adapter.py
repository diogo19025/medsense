import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from control.usuario_control import UsuarioControl
from infra.logger import Logger, LoggerNulo
from infra.logging_adapter import LoggingAdapter


class LoggerEspiao(Logger):
    """Duplo de teste que captura as mensagens recebidas pela porta Logger."""

    def __init__(self):
        self.infos: list[str] = []
        self.avisos: list[str] = []
        self.erros: list[str] = []

    def info(self, mensagem: str) -> None:
        self.infos.append(mensagem)

    def aviso(self, mensagem: str) -> None:
        self.avisos.append(mensagem)

    def erro(self, mensagem: str) -> None:
        self.erros.append(mensagem)


def _dados_responsavel(email="joao@email.com"):
    return {
        "nome": "Joao Silva",
        "login": "joao",
        "email": email,
        "senha": "SenhaForte1",
        "parentesco_principal": "Pai",
    }


class LoggingAdapterTest(unittest.TestCase):
    def test_deve_traduzir_metodos_de_dominio_para_a_stdlib(self):
        adapter = LoggingAdapter(nome="medsense.teste")
        with self.assertLogs("medsense.teste", level="INFO") as captura:
            adapter.info("ola")
            adapter.aviso("cuidado")
            adapter.erro("falhou")

        self.assertIn("INFO:medsense.teste:ola", captura.output)
        self.assertIn("WARNING:medsense.teste:cuidado", captura.output)
        self.assertIn("ERROR:medsense.teste:falhou", captura.output)

    def test_nao_deve_duplicar_handlers_em_reinstanciacao(self):
        LoggingAdapter(nome="medsense.sem-duplicar")
        LoggingAdapter(nome="medsense.sem-duplicar")
        self.assertEqual(len(logging.getLogger("medsense.sem-duplicar").handlers), 1)


class ControlUsaLoggerTest(unittest.TestCase):
    def test_deve_logar_cadastro_de_usuario(self):
        espiao = LoggerEspiao()
        control = UsuarioControl(logger=espiao)

        control.adicionar_responsavel_familiar(_dados_responsavel())

        self.assertTrue(any("Usuario cadastrado" in m for m in espiao.infos))

    def test_deve_operar_sem_logger_injetado(self):
        control = UsuarioControl()
        self.assertIsInstance(control._logger, LoggerNulo)
        control.adicionar_responsavel_familiar(_dados_responsavel())
        self.assertEqual(len(control.listar_usuarios()), 1)


if __name__ == "__main__":
    unittest.main()
