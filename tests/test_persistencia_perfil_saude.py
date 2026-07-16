import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from entity.exceptions import ArquivoPersistenciaError, BancoDadosError
from entity.perfil_saude import PerfilSaude
from infra.persistencia.repositorio_arquivo import RepositorioPerfilSaudeArquivo
from infra.persistencia.repositorio_sqlite import RepositorioPerfilSaudeSQLite


def _perfil(usuario_id="usuario-1"):
    return PerfilSaude(
        usuario_id=usuario_id,
        tipo_sanguineo="O+",
        alergias=["Dipirona", "Amendoim"],
        condicoes_cronicas=["Asma"],
        medicamentos_continuos=["Salbutamol"],
        observacoes="Acompanhamento semestral",
    )


class RepositorioPerfilSaudeArquivoTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._caminho = os.path.join(self._dir.name, "perfis_saude.dat")

    def tearDown(self):
        self._dir.cleanup()

    def test_deve_retornar_lista_vazia_quando_arquivo_nao_existe(self):
        repo = RepositorioPerfilSaudeArquivo(self._caminho)
        self.assertEqual(repo.carregar(), [])

    def test_deve_salvar_e_recarregar_perfis(self):
        repo = RepositorioPerfilSaudeArquivo(self._caminho)
        repo.salvar([_perfil(), _perfil(usuario_id="usuario-2")])

        recarregados = repo.carregar()

        self.assertEqual(len(recarregados), 2)
        self.assertEqual(
            {p.usuario_id for p in recarregados}, {"usuario-1", "usuario-2"}
        )

    def test_deve_lancar_erro_de_io_ao_gravar_em_caminho_invalido(self):
        caminho_invalido = os.path.join(self._dir.name, "nao", "existe", "p.dat")
        repo = RepositorioPerfilSaudeArquivo(caminho_invalido)
        with self.assertRaises(ArquivoPersistenciaError):
            repo.salvar([_perfil()])

    def test_deve_lancar_erro_ao_ler_arquivo_corrompido(self):
        with open(self._caminho, "wb") as arquivo:
            arquivo.write(b"\x00\x01 isto nao e um pickle valido")
        repo = RepositorioPerfilSaudeArquivo(self._caminho)
        with self.assertRaises(ArquivoPersistenciaError):
            repo.carregar()


class RepositorioPerfilSaudeSQLiteTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._caminho = os.path.join(self._dir.name, "medsense.db")

    def tearDown(self):
        self._dir.cleanup()

    def test_deve_salvar_e_recarregar_perfis_preservando_as_listas(self):
        repo = RepositorioPerfilSaudeSQLite(self._caminho)
        repo.salvar([_perfil()])

        (recarregado,) = repo.carregar()

        self.assertEqual(recarregado.tipo_sanguineo, "O+")
        self.assertEqual(recarregado.alergias, ["Dipirona", "Amendoim"])
        self.assertEqual(recarregado.condicoes_cronicas, ["Asma"])
        self.assertEqual(recarregado.medicamentos_continuos, ["Salbutamol"])
        self.assertEqual(recarregado.observacoes, "Acompanhamento semestral")

    def test_deve_preservar_id_e_vinculo_no_round_trip(self):
        repo = RepositorioPerfilSaudeSQLite(self._caminho)
        perfil = _perfil()
        repo.salvar([perfil])

        (recarregado,) = repo.carregar()

        self.assertEqual(recarregado.id, perfil.id)
        self.assertEqual(recarregado.usuario_id, perfil.usuario_id)

    def test_deve_lancar_erro_de_banco_quando_caminho_inacessivel(self):
        # Apontar para um diretório torna o arquivo de banco inabrível.
        with self.assertRaises(BancoDadosError):
            RepositorioPerfilSaudeSQLite(self._dir.name)


if __name__ == "__main__":
    unittest.main()
