import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collection.perfil_saude_collection import PerfilSaudeCollection
from entity.exceptions import PerfilSaudeInvalidoError
from entity.perfil_saude import PerfilSaude
from entity.validador_perfil_saude import ValidadorPerfilSaude


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


if __name__ == "__main__":
    unittest.main()
