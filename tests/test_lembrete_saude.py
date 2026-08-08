import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from control.observadores_lembrete import NotificadorConsole
from entity.exceptions import LembreteSaudeInvalidoError
from entity.lembrete_saude import LembreteSaude, SituacaoLembrete, TipoLembrete


def _lembrete(**campos) -> LembreteSaude:
    dados = {
        "id_lembrete": "L1",
        "usuario_id": "usuario-1",
        "titulo": "Tomar Losartana",
        "descricao": "1 comprimido de 50mg",
        "data_hora": datetime(2026, 8, 10, 8, 0),
        "tipo": TipoLembrete.MEDICAMENTO,
    }
    dados.update(campos)
    return LembreteSaude(**dados)


class ValidacaoLembreteSaudeTest(unittest.TestCase):
    def test_deve_criar_lembrete_com_dados_validos(self):
        lembrete = _lembrete()

        self.assertEqual(lembrete.titulo, "Tomar Losartana")
        self.assertEqual(lembrete.situacao, SituacaoLembrete.PENDENTE)

    def test_deve_remover_espacos_sobrando_do_titulo(self):
        self.assertEqual(_lembrete(titulo="  Tomar Losartana  ").titulo, "Tomar Losartana")

    def test_deve_lancar_erro_quando_identificador_vazio(self):
        with self.assertRaisesRegex(LembreteSaudeInvalidoError, "identificador"):
            _lembrete(id_lembrete="   ")

    def test_deve_lancar_erro_quando_nao_ha_vinculo_com_usuario(self):
        with self.assertRaisesRegex(LembreteSaudeInvalidoError, "vinculado"):
            _lembrete(usuario_id="")

    def test_deve_lancar_erro_quando_titulo_vazio(self):
        with self.assertRaisesRegex(LembreteSaudeInvalidoError, "título"):
            _lembrete(titulo="")

    def test_deve_lancar_erro_quando_data_hora_e_texto(self):
        with self.assertRaisesRegex(LembreteSaudeInvalidoError, "datetime"):
            _lembrete(data_hora="10/07/2026 08:00")

    def test_deve_lancar_erro_quando_data_hora_ausente(self):
        with self.assertRaisesRegex(LembreteSaudeInvalidoError, "datetime"):
            _lembrete(data_hora=None)

    def test_deve_lancar_erro_quando_tipo_nao_e_da_enumeracao(self):
        with self.assertRaisesRegex(LembreteSaudeInvalidoError, "tipo"):
            _lembrete(tipo="medicamento")

    def test_deve_lancar_erro_quando_situacao_nao_e_da_enumeracao(self):
        with self.assertRaisesRegex(LembreteSaudeInvalidoError, "situacao"):
            _lembrete(situacao="pendente")

    # O NotificadorConsole formata data_hora e tipo; um lembrete que nasce
    # validado nunca o faz quebrar com AttributeError.
    def test_lembrete_valido_deve_ser_exibivel_pelo_notificador_console(self):
        saida = io.StringIO()

        with redirect_stdout(saida):
            NotificadorConsole().notificar(_lembrete(), "criado")

        self.assertIn("Tomar Losartana", saida.getvalue())
        self.assertIn("10/08/2026 08:00", saida.getvalue())


class SituacaoLembreteSaudeTest(unittest.TestCase):
    def test_concluir_deve_marcar_o_lembrete_como_concluido(self):
        lembrete = _lembrete()

        lembrete.concluir()

        self.assertEqual(lembrete.situacao, SituacaoLembrete.CONCLUIDO)

    def test_cancelar_deve_marcar_o_lembrete_como_cancelado(self):
        lembrete = _lembrete()

        lembrete.cancelar()

        self.assertEqual(lembrete.situacao, SituacaoLembrete.CANCELADO)


if __name__ == "__main__":
    unittest.main()
