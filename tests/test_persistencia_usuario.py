import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from infra.persistencia.repositorio_arquivo import RepositorioArquivoBinario
from infra.persistencia.repositorio_sqlite import RepositorioSQLite
from infra.persistencia.repositorio_usuario import RepositorioUsuario
from control.usuario_control import UsuarioControl
from entity.exceptions import (
    ArquivoPersistenciaError,
    BancoDadosError,
    PersistenciaError,
)
from entity.familiar_paciente import FamiliarPaciente
from entity.responsavel_familiar import ResponsavelFamiliar


def _responsavel(email="maria@email.com"):
    return ResponsavelFamiliar(
        nome="Maria Silva",
        login="maria",
        email=email,
        senha="SenhaForte1",
        parentesco_principal="Mae",
    )


def _familiar(email="ana@email.com"):
    return FamiliarPaciente(
        nome="Ana Silva",
        login="ana",
        email=email,
        senha="SenhaForte1",
        data_nascimento="2000-01-01",
        parentesco="Filha",
    )


def _dados_responsavel(email="joao@email.com"):
    return {
        "nome": "Joao Silva",
        "login": "joao",
        "email": email,
        "senha": "SenhaForte1",
        "parentesco_principal": "Pai",
    }


class RepositorioArquivoBinarioTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._caminho = os.path.join(self._dir.name, "usuarios.dat")

    def tearDown(self):
        self._dir.cleanup()

    def test_deve_retornar_lista_vazia_quando_arquivo_nao_existe(self):
        repo = RepositorioArquivoBinario(self._caminho)
        self.assertEqual(repo.carregar(), [])

    def test_deve_salvar_e_recarregar_usuarios(self):
        repo = RepositorioArquivoBinario(self._caminho)
        repo.salvar([_responsavel(), _familiar()])

        recarregados = repo.carregar()

        self.assertEqual(len(recarregados), 2)
        self.assertEqual({u.email for u in recarregados}, {"maria@email.com", "ana@email.com"})

    def test_deve_lancar_erro_de_io_ao_gravar_em_caminho_invalido(self):
        caminho_invalido = os.path.join(self._dir.name, "nao", "existe", "u.dat")
        repo = RepositorioArquivoBinario(caminho_invalido)
        with self.assertRaises(ArquivoPersistenciaError):
            repo.salvar([_responsavel()])

    def test_deve_lancar_erro_ao_ler_arquivo_corrompido(self):
        with open(self._caminho, "wb") as arquivo:
            arquivo.write(b"\x00\x01 isto nao e um pickle valido")
        repo = RepositorioArquivoBinario(self._caminho)
        with self.assertRaises(ArquivoPersistenciaError):
            repo.carregar()


class RepositorioSQLiteTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._caminho = os.path.join(self._dir.name, "usuarios.db")

    def tearDown(self):
        self._dir.cleanup()

    def test_deve_salvar_e_recarregar_usuarios(self):
        repo = RepositorioSQLite(self._caminho)
        repo.salvar([_responsavel(), _familiar()])

        recarregados = repo.carregar()

        self.assertEqual(len(recarregados), 2)
        por_email = {u.email: u for u in recarregados}
        self.assertIsInstance(por_email["maria@email.com"], ResponsavelFamiliar)
        self.assertIsInstance(por_email["ana@email.com"], FamiliarPaciente)
        self.assertEqual(por_email["ana@email.com"].parentesco, "Filha")

    def test_deve_preservar_id_no_round_trip(self):
        repo = RepositorioSQLite(self._caminho)
        responsavel = _responsavel()
        repo.salvar([responsavel])

        (recarregado,) = repo.carregar()

        self.assertEqual(recarregado.id, responsavel.id)

    def test_deve_lancar_erro_de_banco_quando_caminho_inacessivel(self):
        # Apontar para um diretório torna o arquivo de banco inabrível.
        with self.assertRaises(BancoDadosError):
            RepositorioSQLite(self._dir.name)


class ControlPersistenciaTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._caminho = os.path.join(self._dir.name, "usuarios.dat")

    def tearDown(self):
        self._dir.cleanup()

    def test_deve_carregar_repositorio_para_a_ram_no_inicio(self):
        repo = RepositorioArquivoBinario(self._caminho)
        primeiro = UsuarioControl(repo)
        primeiro.adicionar_responsavel_familiar(_dados_responsavel())

        segundo = UsuarioControl(repo)

        usuarios = segundo.listar_usuarios()
        self.assertEqual(len(usuarios), 1)
        self.assertEqual(usuarios[0].email, "joao@email.com")

    def test_deve_desfazer_adicao_em_ram_quando_persistencia_falha(self):
        class RepositorioQuebrado(RepositorioUsuario):
            def carregar(self):
                return []

            def salvar(self, usuarios):
                raise ArquivoPersistenciaError("falha simulada de gravação")

        control = UsuarioControl(RepositorioQuebrado())
        with self.assertRaises(PersistenciaError):
            control.adicionar_responsavel_familiar(_dados_responsavel())

        self.assertEqual(control.listar_usuarios(), [])

    def test_sem_repositorio_opera_apenas_em_ram(self):
        control = UsuarioControl()
        control.adicionar_responsavel_familiar(_dados_responsavel())
        self.assertEqual(len(control.listar_usuarios()), 1)


if __name__ == "__main__":
    unittest.main()
