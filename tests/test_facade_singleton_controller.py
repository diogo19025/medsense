import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from control.facade_singleton_controller import FacadeSingletonController
from control.lembrete_control import LembreteControl
from control.perfil_saude_control import PerfilSaudeControl
from control.resumo_saude_builder import DiretorResumoSaude, ResumoSaudeTextoBuilder
from control.usuario_control import UsuarioControl
from entity.lembrete_saude import TipoLembrete


def _dados_familiar_paciente() -> dict:
    return {
        "nome": "Joao",
        "login": "joao",
        "email": "joao@email.com",
        "senha": "Senha!Forte1",
        "data_nascimento": "01/01/2000",
        "parentesco": "Filho",
    }


def _dados_perfil_saude() -> dict:
    return {
        "tipo_sanguineo": "O+",
        "alergias": ["Dipirona"],
        "condicoes_cronicas": [],
        "medicamentos_continuos": [],
        "observacoes": "",
    }


def _dados_lembrete(id_lembrete: str = "lembrete-1") -> dict:
    return {
        "id_lembrete": id_lembrete,
        "titulo": "Tomar remedio",
        "descricao": "Losartana 50mg",
        "data_hora": datetime(2026, 7, 10, 8, 0),
        "tipo": TipoLembrete.MEDICAMENTO,
    }


class FacadeSingletonControllerTest(unittest.TestCase):
    def setUp(self):
        # Cada teste começa com a fachada "zerada", sem instância prévia
        # vazando de outro teste.
        FacadeSingletonController.resetar_instancia()
        self.usuario_control = UsuarioControl()
        self.perfil_control = PerfilSaudeControl(self.usuario_control)
        self.lembrete_control = LembreteControl(self.usuario_control)
        self.diretor_resumo_saude = DiretorResumoSaude(ResumoSaudeTextoBuilder())

    def tearDown(self):
        FacadeSingletonController.resetar_instancia()

    def _obter_instancia(self) -> FacadeSingletonController:
        return FacadeSingletonController.obter_instancia(
            self.usuario_control,
            self.perfil_control,
            self.lembrete_control,
            self.diretor_resumo_saude,
        )

    # ----- Comportamento de Singleton -----

    def test_deve_criar_instancia_na_primeira_chamada(self):
        facade = self._obter_instancia()
        self.assertIsInstance(facade, FacadeSingletonController)

    def test_deve_devolver_a_mesma_instancia_em_chamadas_seguintes(self):
        primeira = self._obter_instancia()
        segunda = FacadeSingletonController.obter_instancia()

        self.assertIs(primeira, segunda)

    def test_deve_ignorar_novos_controllers_apos_a_primeira_chamada(self):
        self._obter_instancia()
        outro_usuario_control = UsuarioControl()
        outro_perfil_control = PerfilSaudeControl(outro_usuario_control)
        outro_lembrete_control = LembreteControl(outro_usuario_control)
        outro_diretor = DiretorResumoSaude(ResumoSaudeTextoBuilder())

        facade = FacadeSingletonController.obter_instancia(
            outro_usuario_control,
            outro_perfil_control,
            outro_lembrete_control,
            outro_diretor,
        )

        # A fachada continua usando os controllers da primeira chamada.
        self.assertEqual(
            facade.listar_usuarios(), self.usuario_control.listar_usuarios()
        )

    def test_deve_lancar_erro_se_primeira_chamada_nao_informar_controllers(self):
        with self.assertRaises(ValueError):
            FacadeSingletonController.obter_instancia()

    # ----- Comportamento de Facade (delegação) -----

    def test_deve_delegar_cadastro_de_usuario_para_usuario_control(self):
        facade = self._obter_instancia()

        facade.adicionar_familiar_paciente(_dados_familiar_paciente())

        self.assertEqual(len(facade.listar_usuarios()), 1)
        self.assertEqual(len(self.usuario_control.listar_usuarios()), 1)

    def test_deve_delegar_cadastro_de_perfil_para_perfil_saude_control(self):
        facade = self._obter_instancia()
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())

        facade.cadastrar_perfil_saude("joao@email.com", _dados_perfil_saude())

        self.assertEqual(len(facade.listar_perfis_saude()), 1)
        self.assertEqual(len(self.perfil_control.listar_perfis()), 1)

    def test_deve_delegar_desfazer_atualizacao_para_historico_de_perfil(self):
        facade = self._obter_instancia()
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())
        facade.cadastrar_perfil_saude("joao@email.com", _dados_perfil_saude())
        facade.atualizar_perfil_saude(
            "joao@email.com", {"tipo_sanguineo": "AB-"}
        )

        perfil_restaurado = facade.desfazer_ultima_atualizacao_perfil()

        self.assertEqual(perfil_restaurado.tipo_sanguineo, "O+")

    def test_deve_delegar_criacao_de_lembrete_para_lembrete_control(self):
        facade = self._obter_instancia()
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())

        facade.criar_lembrete("joao@email.com", _dados_lembrete())

        self.assertEqual(len(facade.listar_lembretes()), 1)
        self.assertEqual(len(self.lembrete_control.listar_lembretes()), 1)

    def test_deve_delegar_conclusao_de_lembrete_para_lembrete_control(self):
        facade = self._obter_instancia()
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())
        facade.criar_lembrete("joao@email.com", _dados_lembrete())

        facade.concluir_lembrete("lembrete-1")

        lembrete = facade.listar_lembretes()[0]
        self.assertEqual(lembrete.situacao.value, "concluído")

    def test_deve_gerar_resumo_de_saude_basico_via_diretor(self):
        facade = self._obter_instancia()
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())
        facade.cadastrar_perfil_saude("joao@email.com", _dados_perfil_saude())

        resumo = facade.gerar_resumo_saude_basico("joao@email.com")

        self.assertEqual(resumo.formato, "texto")
        self.assertIn("Joao", resumo.conteudo)
        self.assertIn("O+", resumo.conteudo)

    def test_deve_trocar_formato_do_resumo_de_saude(self):
        from control.resumo_saude_builder import ResumoSaudeHTMLBuilder

        facade = self._obter_instancia()
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())

        facade.definir_formato_resumo_saude(ResumoSaudeHTMLBuilder())
        resumo = facade.gerar_resumo_saude_basico("joao@email.com")

        self.assertEqual(resumo.formato, "html")
        self.assertIn("<h1>", resumo.conteudo)

    # ----- Método de contagem agregada -----

    def test_quantidade_total_entidades_deve_comecar_em_zero(self):
        facade = self._obter_instancia()

        self.assertEqual(facade.quantidade_total_entidades(), 0)

    def test_quantidade_total_entidades_deve_somar_usuarios_perfis_e_lembretes(self):
        facade = self._obter_instancia()
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())
        facade.cadastrar_perfil_saude("joao@email.com", _dados_perfil_saude())
        facade.criar_lembrete("joao@email.com", _dados_lembrete())

        self.assertEqual(facade.quantidade_total_entidades(), 3)


if __name__ == "__main__":
    unittest.main()