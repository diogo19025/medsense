import os
import sys
import unittest
from dataclasses import FrozenInstanceError
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from control.resumo_saude_builder import (
    SECAO_CONSULTAS,
    SECAO_DADOS_USUARIO,
    SECAO_DOCUMENTOS,
    SECAO_MEDICAMENTOS,
    SECAO_PERFIL_SAUDE,
    SECAO_VACINAS,
    DiretorResumoSaude,
    ResumoSaudeHTMLBuilder,
    ResumoSaudeTextoBuilder,
)
from entity.familiar_paciente import FamiliarPaciente
from entity.perfil_saude import PerfilSaude
from entity.resumo_saude import ResumoSaude


def _usuario(nome="Ana Silva", login="ana"):
    return FamiliarPaciente(
        nome=nome,
        login=login,
        email="ana@email.com",
        senha="SenhaForte1",
        data_nascimento="2000-01-01",
        parentesco="Filha",
    )


def _perfil(usuario_id="usuario-1", **campos):
    dados = {
        "tipo_sanguineo": "O+",
        "alergias": ["Dipirona"],
        "condicoes_cronicas": ["Asma"],
        "medicamentos_continuos": ["Salbutamol"],
        "observacoes": "Acompanhamento semestral",
    }
    dados.update(campos)
    return PerfilSaude(usuario_id=usuario_id, **dados)


class ResumoSaudeTest(unittest.TestCase):
    def test_deve_guardar_o_documento_montado(self):
        resumo = ResumoSaude(
            usuario_id="usuario-1",
            formato="texto",
            conteudo="conteudo montado",
            secoes=(SECAO_DADOS_USUARIO,),
        )
        self.assertEqual(resumo.usuario_id, "usuario-1")
        self.assertEqual(resumo.formato, "texto")
        self.assertEqual(resumo.conteudo, "conteudo montado")
        self.assertEqual(resumo.secoes, (SECAO_DADOS_USUARIO,))

    def test_deve_iniciar_sem_secoes_e_com_momento_de_geracao(self):
        resumo = ResumoSaude(usuario_id="usuario-1", formato="texto", conteudo="")
        self.assertEqual(resumo.secoes, ())
        self.assertIsInstance(resumo.gerado_em, datetime)

    def test_nao_deve_permitir_alterar_o_resumo_depois_de_pronto(self):
        resumo = ResumoSaude(usuario_id="usuario-1", formato="texto", conteudo="")
        with self.assertRaises(FrozenInstanceError):
            resumo.conteudo = "outro"


class ResumoSaudeTextoBuilderTest(unittest.TestCase):
    def setUp(self):
        self._builder = ResumoSaudeTextoBuilder()

    def test_deve_informar_o_formato_produzido(self):
        self.assertEqual(self._builder.formato, "texto")

    def test_deve_vincular_o_resumo_ao_usuario(self):
        usuario = _usuario()

        self._builder.construir_dados_usuario(usuario)

        self.assertEqual(self._builder.obter_resultado().usuario_id, usuario.id)

    def test_deve_incluir_os_dados_do_usuario(self):
        self._builder.construir_dados_usuario(_usuario())

        conteudo = self._builder.obter_resultado().conteudo

        self.assertIn("Ana Silva", conteudo)
        self.assertIn("ana@email.com", conteudo)
        self.assertIn("FAMILIAR_PACIENTE", conteudo)

    def test_deve_incluir_os_dados_do_perfil_de_saude(self):
        self._builder.construir_perfil_saude(_perfil())

        conteudo = self._builder.obter_resultado().conteudo

        self.assertIn("O+", conteudo)
        self.assertIn("Dipirona", conteudo)
        self.assertIn("Asma", conteudo)
        self.assertIn("Salbutamol", conteudo)

    def test_deve_avisar_quando_o_paciente_nao_tem_perfil(self):
        self._builder.construir_perfil_saude(None)

        resumo = self._builder.obter_resultado()

        self.assertIn(SECAO_PERFIL_SAUDE, resumo.secoes)
        self.assertIn("nao possui perfil de saude", resumo.conteudo)

    def test_deve_exibir_tracos_para_listas_vazias_do_perfil(self):
        self._builder.construir_perfil_saude(
            _perfil(alergias=[], condicoes_cronicas=[], observacoes="")
        )

        conteudo = self._builder.obter_resultado().conteudo

        self.assertIn("Alergias..............: -", conteudo)
        self.assertIn("Observacoes...........: -", conteudo)

    def test_deve_incluir_a_secao_opcional_quando_ha_itens(self):
        self._builder.construir_medicamentos(["Dipirona 500mg"])

        resumo = self._builder.obter_resultado()

        self.assertEqual(resumo.secoes, (SECAO_MEDICAMENTOS,))
        self.assertIn("  - Dipirona 500mg", resumo.conteudo)

    def test_deve_omitir_a_secao_opcional_quando_nao_ha_itens(self):
        self._builder.construir_medicamentos([])
        self._builder.construir_vacinas([])
        self._builder.construir_consultas([])
        self._builder.construir_documentos([])

        resumo = self._builder.obter_resultado()

        self.assertEqual(resumo.secoes, ())
        self.assertNotIn(SECAO_MEDICAMENTOS, resumo.conteudo)

    def test_deve_montar_o_cabecalho_e_o_rodape(self):
        self._builder.construir_cabecalho()
        self._builder.construir_rodape()

        conteudo = self._builder.obter_resultado().conteudo

        self.assertTrue(conteudo.startswith("MedSense - Resumo de Saude"))
        self.assertIn("Gerado em", conteudo)

    def test_passos_devem_permitir_encadeamento(self):
        resumo = (
            self._builder.construir_cabecalho()
            .construir_dados_usuario(_usuario())
            .construir_perfil_saude(_perfil())
            .construir_rodape()
            .obter_resultado()
        )

        self.assertEqual(resumo.secoes, (SECAO_DADOS_USUARIO, SECAO_PERFIL_SAUDE))

    def test_deve_reiniciar_depois_de_entregar_o_resultado(self):
        self._builder.construir_medicamentos(["Dipirona 500mg"])
        self._builder.obter_resultado()

        segundo = self._builder.obter_resultado()

        self.assertEqual(segundo.secoes, ())
        self.assertNotIn("Dipirona", segundo.conteudo)

    def test_reiniciar_deve_descartar_o_documento_em_construcao(self):
        self._builder.construir_dados_usuario(_usuario())

        resumo = self._builder.reiniciar().obter_resultado()

        self.assertEqual(resumo.secoes, ())
        self.assertEqual(resumo.usuario_id, "")


class ResumoSaudeHTMLBuilderTest(unittest.TestCase):
    def setUp(self):
        self._builder = ResumoSaudeHTMLBuilder()

    def test_deve_informar_o_formato_produzido(self):
        self.assertEqual(self._builder.formato, "html")

    def test_deve_gerar_documento_html_valido(self):
        self._builder.construir_cabecalho()
        self._builder.construir_dados_usuario(_usuario())
        self._builder.construir_rodape()

        conteudo = self._builder.obter_resultado().conteudo

        self.assertTrue(conteudo.startswith("<!DOCTYPE html>"))
        self.assertIn("<h1>", conteudo)
        self.assertIn("<li>Nome: <strong>Ana Silva</strong></li>", conteudo)
        self.assertTrue(conteudo.rstrip().endswith("</html>"))

    def test_deve_listar_os_itens_da_secao_opcional(self):
        self._builder.construir_vacinas(["Gripe 2026", "Hepatite B"])

        resumo = self._builder.obter_resultado()

        self.assertEqual(resumo.secoes, (SECAO_VACINAS,))
        self.assertIn("<li>Gripe 2026</li>", resumo.conteudo)
        self.assertIn("<li>Hepatite B</li>", resumo.conteudo)

    def test_deve_omitir_a_secao_opcional_quando_nao_ha_itens(self):
        self._builder.construir_consultas([])

        resumo = self._builder.obter_resultado()

        self.assertEqual(resumo.secoes, ())
        self.assertNotIn("<h2>Consultas</h2>", resumo.conteudo)

    def test_deve_escapar_o_conteudo_vindo_do_usuario(self):
        self._builder.construir_dados_usuario(_usuario(nome="<script>alerta</script>"))

        conteudo = self._builder.obter_resultado().conteudo

        self.assertIn("&lt;script&gt;", conteudo)
        self.assertNotIn("<script>", conteudo)


class DiretorResumoSaudeTest(unittest.TestCase):
    def setUp(self):
        self._diretor = DiretorResumoSaude(ResumoSaudeTextoBuilder())
        self._usuario = _usuario()
        self._perfil = _perfil(usuario_id=self._usuario.id)

    def test_resumo_basico_deve_ter_apenas_usuario_e_perfil(self):
        resumo = self._diretor.construir_resumo_basico(self._usuario, self._perfil)

        self.assertEqual(resumo.secoes, (SECAO_DADOS_USUARIO, SECAO_PERFIL_SAUDE))
        self.assertEqual(resumo.usuario_id, self._usuario.id)
        self.assertIn("Ana Silva", resumo.conteudo)
        self.assertIn("O+", resumo.conteudo)

    def test_resumo_completo_deve_incluir_as_secoes_opcionais_informadas(self):
        resumo = self._diretor.construir_resumo_completo(
            self._usuario,
            self._perfil,
            medicamentos=["Dipirona 500mg"],
            vacinas=["Gripe 2026"],
            consultas=["10/01/2026 - Cardiologista"],
            documentos=["Exame de sangue"],
        )

        self.assertEqual(
            resumo.secoes,
            (
                SECAO_DADOS_USUARIO,
                SECAO_PERFIL_SAUDE,
                SECAO_MEDICAMENTOS,
                SECAO_VACINAS,
                SECAO_CONSULTAS,
                SECAO_DOCUMENTOS,
            ),
        )
        self.assertIn("Exame de sangue", resumo.conteudo)

    def test_resumo_completo_sem_secoes_opcionais_deve_igualar_o_basico(self):
        completo = self._diretor.construir_resumo_completo(self._usuario, self._perfil)
        basico = self._diretor.construir_resumo_basico(self._usuario, self._perfil)

        self.assertEqual(completo.secoes, basico.secoes)

    def test_resumo_completo_deve_omitir_as_secoes_opcionais_vazias(self):
        resumo = self._diretor.construir_resumo_completo(
            self._usuario, self._perfil, vacinas=["Gripe 2026"], consultas=[]
        )

        self.assertEqual(
            resumo.secoes, (SECAO_DADOS_USUARIO, SECAO_PERFIL_SAUDE, SECAO_VACINAS)
        )

    def test_deve_gerar_resumo_para_paciente_sem_perfil(self):
        resumo = self._diretor.construir_resumo_basico(self._usuario, None)

        self.assertEqual(resumo.secoes, (SECAO_DADOS_USUARIO, SECAO_PERFIL_SAUDE))
        self.assertIn("nao possui perfil de saude", resumo.conteudo)

    def test_a_mesma_receita_deve_valer_para_os_dois_formatos(self):
        # O diretor fixa a ordem das seções; trocar o builder muda só o formato.
        texto = self._diretor.construir_resumo_completo(
            self._usuario, self._perfil, medicamentos=["Dipirona 500mg"]
        )

        self._diretor.builder = ResumoSaudeHTMLBuilder()
        html = self._diretor.construir_resumo_completo(
            self._usuario, self._perfil, medicamentos=["Dipirona 500mg"]
        )

        self.assertEqual(texto.secoes, html.secoes)
        self.assertEqual(texto.usuario_id, html.usuario_id)
        self.assertEqual(html.formato, "html")
        self.assertNotEqual(texto.conteudo, html.conteudo)

    def test_deve_reaproveitar_o_diretor_para_varios_resumos(self):
        primeiro = self._diretor.construir_resumo_completo(
            self._usuario, self._perfil, vacinas=["Gripe 2026"]
        )
        segundo = self._diretor.construir_resumo_basico(self._usuario, self._perfil)

        self.assertIn(SECAO_VACINAS, primeiro.secoes)
        self.assertNotIn(SECAO_VACINAS, segundo.secoes)

    def test_deve_rejeitar_perfil_de_outro_usuario_nas_duas_receitas(self):
        perfil_de_outro_usuario = _perfil(usuario_id="outro-usuario")
        receitas = (
            self._diretor.construir_resumo_basico,
            self._diretor.construir_resumo_completo,
        )

        for receita in receitas:
            with self.subTest(receita=receita.__name__):
                with self.assertRaisesRegex(ValueError, "nao pertence"):
                    receita(self._usuario, perfil_de_outro_usuario)

    def test_rodape_e_produto_devem_usar_o_mesmo_momento(self):
        momento = datetime(2026, 8, 6, 14, 30, 45)

        for builder_class in (ResumoSaudeTextoBuilder, ResumoSaudeHTMLBuilder):
            with self.subTest(builder=builder_class.__name__):
                with patch(
                    "control.resumo_saude_builder.datetime"
                ) as datetime_mock:
                    datetime_mock.now.return_value = momento
                    diretor = DiretorResumoSaude(builder_class())
                    resumo = diretor.construir_resumo_basico(
                        self._usuario, self._perfil
                    )

                self.assertEqual(resumo.gerado_em, momento)
                self.assertIn(
                    momento.strftime("%d/%m/%Y %H:%M:%S"),
                    resumo.conteudo,
                )


if __name__ == "__main__":
    unittest.main()
