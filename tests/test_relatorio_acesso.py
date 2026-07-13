import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from control.relatorio_acesso import (
    RelatorioAcesso,
    RelatorioAcessoHTML,
    RelatorioAcessoTexto,
    criar_relatorio,
)
from control.usuario_control import UsuarioControl
from entity.registro_acesso import RegistroAcesso


def _registros():
    return [
        RegistroAcesso("1", "joao", "RESPONSAVEL_FAMILIAR", momento=datetime(2026, 7, 1, 8, 0)),
        RegistroAcesso("1", "joao", "RESPONSAVEL_FAMILIAR", momento=datetime(2026, 7, 2, 9, 0)),
        RegistroAcesso("2", "ana", "FAMILIAR_PACIENTE", momento=datetime(2026, 7, 3, 10, 0)),
    ]


class EstatisticasTest(unittest.TestCase):
    def test_deve_calcular_estatisticas_agregadas(self):
        relatorio = RelatorioAcessoTexto(_registros())
        estat = relatorio._calcular_estatisticas()

        self.assertEqual(estat.total_acessos, 3)
        self.assertEqual(estat.usuarios_distintos, 2)
        self.assertEqual(estat.acessos_por_login, {"joao": 2, "ana": 1})
        self.assertEqual(
            estat.acessos_por_tipo, {"RESPONSAVEL_FAMILIAR": 2, "FAMILIAR_PACIENTE": 1}
        )
        self.assertEqual(estat.primeiro_acesso, datetime(2026, 7, 1, 8, 0))
        self.assertEqual(estat.ultimo_acesso, datetime(2026, 7, 3, 10, 0))
        self.assertEqual(estat.usuario_mais_ativo, "joao")

    def test_deve_lidar_com_lista_vazia(self):
        estat = RelatorioAcessoTexto([])._calcular_estatisticas()
        self.assertEqual(estat.total_acessos, 0)
        self.assertIsNone(estat.primeiro_acesso)
        self.assertIsNone(estat.usuario_mais_ativo)


class TemplateMethodTest(unittest.TestCase):
    def test_texto_deve_conter_numeros_de_acesso(self):
        saida = RelatorioAcessoTexto(_registros()).gerar()
        self.assertIn("Total de acessos", saida)
        self.assertIn("joao: 2", saida)
        self.assertIn("ana: 1", saida)

    def test_html_deve_ser_documento_html_valido(self):
        saida = RelatorioAcessoHTML(_registros()).gerar()
        self.assertTrue(saida.startswith("<!DOCTYPE html>"))
        self.assertIn("<h1>", saida)
        self.assertIn("<td>joao</td><td>2</td>", saida)

    def test_ambos_formatos_usam_mesmas_estatisticas(self):
        # O template method garante o mesmo cálculo; muda só a formatação.
        registros = _registros()
        texto = RelatorioAcessoTexto(registros)._calcular_estatisticas()
        html = RelatorioAcessoHTML(registros)._calcular_estatisticas()
        self.assertEqual(texto, html)

    def test_extensoes_por_formato(self):
        self.assertEqual(RelatorioAcessoTexto([]).extensao, "txt")
        self.assertEqual(RelatorioAcessoHTML([]).extensao, "html")


class FabricaRelatorioTest(unittest.TestCase):
    def test_deve_criar_relatorio_por_formato(self):
        self.assertIsInstance(criar_relatorio("texto", []), RelatorioAcessoTexto)
        self.assertIsInstance(criar_relatorio("HTML", []), RelatorioAcessoHTML)

    def test_deve_lancar_erro_para_formato_desconhecido(self):
        with self.assertRaises(ValueError):
            criar_relatorio("pdf", [])


class ControlRelatorioTest(unittest.TestCase):
    def test_deve_registrar_acesso_e_gerar_relatorio(self):
        control = UsuarioControl()
        control.adicionar_responsavel_familiar(
            {
                "nome": "Joao",
                "login": "joao",
                "email": "joao@email.com",
                "senha": "SenhaForte1",
                "parentesco_principal": "Pai",
            }
        )
        control.registrar_acesso("joao@email.com")
        control.registrar_acesso("joao@email.com")

        self.assertEqual(len(control.listar_acessos()), 2)
        relatorio = control.gerar_relatorio_acessos("texto")
        self.assertIn("joao: 2", relatorio)

    def test_registrar_acesso_de_email_inexistente_deve_falhar(self):
        control = UsuarioControl()
        with self.assertRaises(ValueError):
            control.registrar_acesso("nao@existe.com")


if __name__ == "__main__":
    unittest.main()
