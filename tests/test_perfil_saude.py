import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collection.perfil_saude_collection import PerfilSaudeCollection
from collection.repositorio_perfil_saude import RepositorioPerfilSaude
from control.perfil_saude_control import PerfilSaudeControl
from control.usuario_control import UsuarioControl
from entity.exceptions import PerfilSaudeInvalidoError, PersistenciaError
from entity.perfil_saude import PerfilSaude
from entity.validador_perfil_saude import ValidadorPerfilSaude
from infra.persistencia.repositorio_memoria import RepositorioPerfilSaudeMemoria


def _perfil(usuario_id="usuario-1", tipo_sanguineo="O+", **campos):
    return PerfilSaude(
        usuario_id=usuario_id,
        tipo_sanguineo=tipo_sanguineo,
        **campos,
    )


class ValidadorPerfilSaudeTest(unittest.TestCase):
    def test_deve_aceitar_tipo_sanguineo_valido(self):
        ValidadorPerfilSaude.validar_tipo_sanguineo("AB-")

    def test_deve_lancar_erro_quando_tipo_sanguineo_invalido(self):
        with self.assertRaises(PerfilSaudeInvalidoError):
            ValidadorPerfilSaude.validar_tipo_sanguineo("Z+")

    def test_deve_lancar_erro_quando_usuario_id_vazio(self):
        with self.assertRaises(PerfilSaudeInvalidoError):
            ValidadorPerfilSaude.validar_usuario_id("   ")


class CriarPerfilSaudeTest(unittest.TestCase):
    def test_deve_criar_perfil_com_dados_validos(self):
        perfil = _perfil(
            alergias=["Dipirona"],
            condicoes_cronicas=["Asma"],
            medicamentos_continuos=["Salbutamol"],
            observacoes="Acompanhamento semestral",
        )
        self.assertEqual(perfil.usuario_id, "usuario-1")
        self.assertEqual(perfil.tipo_sanguineo, "O+")
        self.assertEqual(perfil.alergias, ["Dipirona"])

    def test_deve_iniciar_listas_vazias_por_padrao(self):
        perfil = _perfil()
        self.assertEqual(perfil.alergias, [])
        self.assertEqual(perfil.condicoes_cronicas, [])
        self.assertEqual(perfil.medicamentos_continuos, [])
        self.assertEqual(perfil.observacoes, "")

    def test_deve_normalizar_tipo_sanguineo_para_maiusculas(self):
        perfil = _perfil(tipo_sanguineo=" ab+ ")
        self.assertEqual(perfil.tipo_sanguineo, "AB+")

    def test_deve_lancar_erro_ao_criar_perfil_com_tipo_sanguineo_invalido(self):
        with self.assertRaises(PerfilSaudeInvalidoError):
            _perfil(tipo_sanguineo="X-")

    def test_deve_lancar_erro_ao_criar_perfil_sem_usuario(self):
        with self.assertRaises(PerfilSaudeInvalidoError):
            _perfil(usuario_id="")

    def test_deve_gerar_ids_distintos_para_perfis_distintos(self):
        self.assertNotEqual(_perfil().id, _perfil().id)


class PerfilSaudeCollectionTest(unittest.TestCase):
    def setUp(self):
        self._collection = PerfilSaudeCollection()

    def test_deve_adicionar_e_buscar_perfil_por_usuario(self):
        perfil = _perfil()
        self._collection.adicionar(perfil)
        self.assertIs(self._collection.buscar_por_usuario("usuario-1"), perfil)

    def test_deve_retornar_none_quando_usuario_nao_tem_perfil(self):
        self.assertIsNone(self._collection.buscar_por_usuario("desconhecido"))

    def test_deve_lancar_erro_quando_usuario_ja_tem_perfil(self):
        self._collection.adicionar(_perfil())
        with self.assertRaises(ValueError):
            self._collection.adicionar(_perfil(tipo_sanguineo="A-"))

    def test_deve_listar_copia_de_todos_os_perfis(self):
        self._collection.adicionar(_perfil())
        self._collection.adicionar(_perfil(usuario_id="usuario-2"))

        listados = self._collection.listar_todos()
        listados.clear()

        self.assertEqual(self._collection.quantidade(), 2)

    def test_deve_atualizar_perfil_existente_preservando_a_ordem(self):
        self._collection.adicionar(_perfil())
        self._collection.adicionar(_perfil(usuario_id="usuario-2"))

        self._collection.atualizar(_perfil(tipo_sanguineo="AB+"))

        primeiro = self._collection.listar_todos()[0]
        self.assertEqual(primeiro.usuario_id, "usuario-1")
        self.assertEqual(primeiro.tipo_sanguineo, "AB+")

    def test_deve_lancar_erro_ao_atualizar_perfil_inexistente(self):
        with self.assertRaises(ValueError):
            self._collection.atualizar(_perfil())

    def test_deve_remover_perfil_pelo_id(self):
        perfil = _perfil()
        self._collection.adicionar(perfil)
        self._collection.remover(perfil)
        self.assertEqual(self._collection.quantidade(), 0)

    def test_remover_perfil_inexistente_nao_tem_efeito(self):
        self._collection.adicionar(_perfil())
        self._collection.remover(_perfil(usuario_id="usuario-2"))
        self.assertEqual(self._collection.quantidade(), 1)


EMAIL_PACIENTE = "ana@email.com"
EMAIL_RESPONSAVEL = "maria@email.com"


def _dados_perfil(**campos):
    dados = {
        "tipo_sanguineo": "O+",
        "alergias": ["Dipirona"],
        "condicoes_cronicas": ["Asma"],
        "medicamentos_continuos": ["Salbutamol"],
        "observacoes": "Acompanhamento semestral",
    }
    dados.update(campos)
    return dados


def _usuario_control():
    usuarios = UsuarioControl()
    usuarios.adicionar_familiar_paciente(
        {
            "nome": "Ana Silva",
            "login": "ana",
            "email": EMAIL_PACIENTE,
            "senha": "SenhaForte1",
            "data_nascimento": "2000-01-01",
            "parentesco": "Filha",
        }
    )
    usuarios.adicionar_responsavel_familiar(
        {
            "nome": "Maria Silva",
            "login": "maria",
            "email": EMAIL_RESPONSAVEL,
            "senha": "SenhaForte1",
            "parentesco_principal": "Mae",
        }
    )
    return usuarios


class PerfilSaudeControlTest(unittest.TestCase):
    def setUp(self):
        self._control = PerfilSaudeControl(_usuario_control())

    def test_deve_cadastrar_e_buscar_perfil_do_paciente(self):
        cadastrado = self._control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())

        buscado = self._control.buscar_perfil(EMAIL_PACIENTE)

        self.assertIs(buscado, cadastrado)
        self.assertEqual(buscado.tipo_sanguineo, "O+")

    def test_buscar_retorna_none_quando_paciente_nao_tem_perfil(self):
        self.assertIsNone(self._control.buscar_perfil(EMAIL_PACIENTE))

    def test_deve_lancar_erro_ao_cadastrar_para_email_inexistente(self):
        with self.assertRaises(ValueError):
            self._control.cadastrar_perfil("nao@existe.com", _dados_perfil())

    def test_deve_lancar_erro_ao_cadastrar_para_usuario_que_nao_e_paciente(self):
        with self.assertRaises(ValueError):
            self._control.cadastrar_perfil(EMAIL_RESPONSAVEL, _dados_perfil())

    def test_deve_lancar_erro_ao_cadastrar_segundo_perfil_para_o_paciente(self):
        self._control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())
        with self.assertRaises(ValueError):
            self._control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())

    def test_deve_listar_todos_os_perfis(self):
        self._control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())
        self.assertEqual(len(self._control.listar_perfis()), 1)

    def test_deve_atualizar_somente_os_campos_informados(self):
        cadastrado = self._control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())

        atualizado = self._control.atualizar_perfil(
            EMAIL_PACIENTE, {"tipo_sanguineo": "AB-", "alergias": []}
        )

        self.assertEqual(atualizado.tipo_sanguineo, "AB-")
        self.assertEqual(atualizado.alergias, [])
        self.assertEqual(atualizado.condicoes_cronicas, ["Asma"])
        self.assertEqual(atualizado.id, cadastrado.id)

    def test_deve_lancar_erro_ao_atualizar_perfil_inexistente(self):
        with self.assertRaises(ValueError):
            self._control.atualizar_perfil(EMAIL_PACIENTE, {"tipo_sanguineo": "A+"})

    def test_deve_remover_perfil_do_paciente(self):
        self._control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())

        self._control.remover_perfil(EMAIL_PACIENTE)

        self.assertIsNone(self._control.buscar_perfil(EMAIL_PACIENTE))
        self.assertEqual(self._control.listar_perfis(), [])

    def test_deve_lancar_erro_ao_remover_perfil_inexistente(self):
        with self.assertRaises(ValueError):
            self._control.remover_perfil(EMAIL_PACIENTE)


class PerfilSaudeControlPersistenciaTest(unittest.TestCase):
    def setUp(self):
        self._usuarios = _usuario_control()

    def test_deve_carregar_repositorio_para_a_ram_no_inicio(self):
        repositorio = RepositorioPerfilSaudeMemoria()
        primeiro = PerfilSaudeControl(self._usuarios, repositorio)
        primeiro.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())

        segundo = PerfilSaudeControl(self._usuarios, repositorio)

        self.assertEqual(len(segundo.listar_perfis()), 1)

    def _control_quebrado(self, falhar_a_partir_de: int):
        # Repositório que passa a falhar após N gravações bem-sucedidas,
        # para exercitar o desfazer-em-falha de cada operação do CRUD.
        class RepositorioQuebrado(RepositorioPerfilSaude):
            def __init__(self):
                self._gravacoes = 0

            def carregar(self):
                return []

            def salvar(self, perfis):
                self._gravacoes += 1
                if self._gravacoes > falhar_a_partir_de:
                    raise PersistenciaError("falha simulada de gravação")

        return PerfilSaudeControl(self._usuarios, RepositorioQuebrado())

    def test_deve_desfazer_cadastro_em_ram_quando_persistencia_falha(self):
        control = self._control_quebrado(falhar_a_partir_de=0)

        with self.assertRaises(PersistenciaError):
            control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())

        self.assertEqual(control.listar_perfis(), [])

    def test_deve_desfazer_atualizacao_em_ram_quando_persistencia_falha(self):
        control = self._control_quebrado(falhar_a_partir_de=1)
        control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())

        with self.assertRaises(PersistenciaError):
            control.atualizar_perfil(EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"})

        self.assertEqual(
            control.buscar_perfil(EMAIL_PACIENTE).tipo_sanguineo, "O+"
        )

    def test_deve_desfazer_remocao_em_ram_quando_persistencia_falha(self):
        control = self._control_quebrado(falhar_a_partir_de=1)
        control.cadastrar_perfil(EMAIL_PACIENTE, _dados_perfil())

        with self.assertRaises(PersistenciaError):
            control.remover_perfil(EMAIL_PACIENTE)

        self.assertIsNotNone(control.buscar_perfil(EMAIL_PACIENTE))


if __name__ == "__main__":
    unittest.main()
