import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from control.facade_singleton_controller import FacadeSingletonController
from control.perfil_saude_control import PerfilSaudeControl
from control.usuario_control import UsuarioControl


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


class FacadeSingletonControllerTest(unittest.TestCase):
    def setUp(self):
        # Cada teste começa com a fachada "zerada", sem instância prévia
        # vazando de outro teste.
        FacadeSingletonController.resetar_instancia()
        self.usuario_control = UsuarioControl()
        self.perfil_control = PerfilSaudeControl(self.usuario_control)

    def tearDown(self):
        FacadeSingletonController.resetar_instancia()

    # ----- Comportamento de Singleton -----

    def test_deve_criar_instancia_na_primeira_chamada(self):
        facade = FacadeSingletonController.obter_instancia(
            self.usuario_control, self.perfil_control
        )
        self.assertIsInstance(facade, FacadeSingletonController)

    def test_deve_devolver_a_mesma_instancia_em_chamadas_seguintes(self):
        primeira = FacadeSingletonController.obter_instancia(
            self.usuario_control, self.perfil_control
        )
        segunda = FacadeSingletonController.obter_instancia()

        self.assertIs(primeira, segunda)

    def test_deve_ignorar_novos_controllers_apos_a_primeira_chamada(self):
        FacadeSingletonController.obter_instancia(
            self.usuario_control, self.perfil_control
        )
        outro_usuario_control = UsuarioControl()
        outro_perfil_control = PerfilSaudeControl(outro_usuario_control)

        facade = FacadeSingletonController.obter_instancia(
            outro_usuario_control, outro_perfil_control
        )

        # A fachada continua usando os controllers da primeira chamada.
        self.assertEqual(facade.listar_usuarios(), self.usuario_control.listar_usuarios())

    def test_deve_lancar_erro_se_primeira_chamada_nao_informar_controllers(self):
        with self.assertRaises(ValueError):
            FacadeSingletonController.obter_instancia()

    # ----- Comportamento de Facade (delegação) -----

    def test_deve_delegar_cadastro_de_usuario_para_usuario_control(self):
        facade = FacadeSingletonController.obter_instancia(
            self.usuario_control, self.perfil_control
        )

        facade.adicionar_familiar_paciente(_dados_familiar_paciente())

        self.assertEqual(len(facade.listar_usuarios()), 1)
        self.assertEqual(len(self.usuario_control.listar_usuarios()), 1)

    def test_deve_delegar_cadastro_de_perfil_para_perfil_saude_control(self):
        facade = FacadeSingletonController.obter_instancia(
            self.usuario_control, self.perfil_control
        )
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())

        facade.cadastrar_perfil_saude("joao@email.com", _dados_perfil_saude())

        self.assertEqual(len(facade.listar_perfis_saude()), 1)
        self.assertEqual(len(self.perfil_control.listar_perfis()), 1)

    # ----- Método de contagem agregada -----

    def test_quantidade_total_entidades_deve_comecar_em_zero(self):
        facade = FacadeSingletonController.obter_instancia(
            self.usuario_control, self.perfil_control
        )

        self.assertEqual(facade.quantidade_total_entidades(), 0)

    def test_quantidade_total_entidades_deve_somar_usuarios_e_perfis(self):
        facade = FacadeSingletonController.obter_instancia(
            self.usuario_control, self.perfil_control
        )
        facade.adicionar_familiar_paciente(_dados_familiar_paciente())
        facade.cadastrar_perfil_saude("joao@email.com", _dados_perfil_saude())

        self.assertEqual(facade.quantidade_total_entidades(), 2)


if __name__ == "__main__":
    unittest.main()