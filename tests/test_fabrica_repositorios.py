import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collection.repositorio_acesso import RepositorioAcesso
from control.usuario_control import UsuarioControl
from entity.exceptions import ArquivoPersistenciaError, PersistenciaError
from infra.persistencia.fabrica_repositorios import (
    FabricaRepositoriosArquivo,
    FabricaRepositoriosMemoria,
    FabricaRepositoriosSQLite,
    criar_fabrica,
)
from infra.persistencia.repositorio_arquivo import (
    RepositorioAcessoArquivo,
    RepositorioArquivoBinario,
)
from infra.persistencia.repositorio_memoria import (
    RepositorioAcessoMemoria,
    RepositorioUsuarioMemoria,
)
from infra.persistencia.repositorio_sqlite import (
    RepositorioAcessoSQLite,
    RepositorioSQLite,
)


def _dados_responsavel(email="joao@email.com"):
    return {
        "nome": "Joao Silva",
        "login": "joao",
        "email": email,
        "senha": "SenhaForte1",
        "parentesco_principal": "Pai",
    }


class CriarFabricaTest(unittest.TestCase):
    def test_deve_selecionar_a_fabrica_pelo_nome_do_mecanismo(self):
        self.assertIsInstance(criar_fabrica("memoria"), FabricaRepositoriosMemoria)
        self.assertIsInstance(criar_fabrica("arquivo"), FabricaRepositoriosArquivo)
        self.assertIsInstance(criar_fabrica("sqlite"), FabricaRepositoriosSQLite)

    def test_deve_ignorar_maiusculas_no_nome_do_mecanismo(self):
        self.assertIsInstance(criar_fabrica("SQLite"), FabricaRepositoriosSQLite)

    def test_deve_lancar_erro_para_mecanismo_desconhecido(self):
        with self.assertRaises(ValueError):
            criar_fabrica("nuvem")


class FamiliasDeRepositoriosTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._dir.cleanup()

    def test_fabrica_memoria_deve_criar_familia_em_ram(self):
        fabrica = FabricaRepositoriosMemoria()
        self.assertIsInstance(
            fabrica.criar_repositorio_usuarios(), RepositorioUsuarioMemoria
        )
        self.assertIsInstance(
            fabrica.criar_repositorio_acessos(), RepositorioAcessoMemoria
        )

    def test_fabrica_arquivo_deve_criar_familia_em_arquivo(self):
        fabrica = FabricaRepositoriosArquivo(
            caminho_usuarios=os.path.join(self._dir.name, "u.dat"),
            caminho_acessos=os.path.join(self._dir.name, "a.dat"),
        )
        self.assertIsInstance(
            fabrica.criar_repositorio_usuarios(), RepositorioArquivoBinario
        )
        self.assertIsInstance(
            fabrica.criar_repositorio_acessos(), RepositorioAcessoArquivo
        )

    def test_fabrica_sqlite_deve_criar_familia_no_mesmo_banco(self):
        caminho = os.path.join(self._dir.name, "medsense.db")
        fabrica = FabricaRepositoriosSQLite(caminho)
        self.assertIsInstance(fabrica.criar_repositorio_usuarios(), RepositorioSQLite)
        self.assertIsInstance(
            fabrica.criar_repositorio_acessos(), RepositorioAcessoSQLite
        )
        self.assertTrue(os.path.exists(caminho))


class PersistenciaAcessoTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._dir.cleanup()

    def _fabricas_duraveis(self):
        return [
            FabricaRepositoriosArquivo(
                caminho_usuarios=os.path.join(self._dir.name, "u.dat"),
                caminho_acessos=os.path.join(self._dir.name, "a.dat"),
            ),
            FabricaRepositoriosSQLite(os.path.join(self._dir.name, "m.db")),
        ]

    def _controle(self, fabrica):
        return UsuarioControl(
            repositorio=fabrica.criar_repositorio_usuarios(),
            repositorio_acessos=fabrica.criar_repositorio_acessos(),
        )

    def test_deve_salvar_e_recarregar_acessos_em_cada_familia(self):
        for fabrica in self._fabricas_duraveis():
            with self.subTest(fabrica=type(fabrica).__name__):
                primeiro = self._controle(fabrica)
                primeiro.adicionar_responsavel_familiar(_dados_responsavel())
                primeiro.registrar_acesso("joao@email.com")

                segundo = self._controle(fabrica)

                acessos = segundo.listar_acessos()
                self.assertEqual(len(acessos), 1)
                self.assertEqual(acessos[0].login, "joao")
                self.assertEqual(acessos[0].acao, "LOGIN")

    def test_deve_preservar_momento_do_acesso_no_round_trip_sqlite(self):
        fabrica = FabricaRepositoriosSQLite(os.path.join(self._dir.name, "m.db"))
        primeiro = self._controle(fabrica)
        primeiro.adicionar_responsavel_familiar(_dados_responsavel())
        registro = primeiro.registrar_acesso("joao@email.com")

        (recarregado,) = self._controle(fabrica).listar_acessos()

        self.assertEqual(recarregado.momento, registro.momento)

    def test_deve_desfazer_registro_em_ram_quando_persistencia_falha(self):
        class RepositorioAcessoQuebrado(RepositorioAcesso):
            def carregar(self):
                return []

            def salvar(self, registros):
                raise ArquivoPersistenciaError("falha simulada de gravação")

        control = UsuarioControl(
            repositorio_acessos=RepositorioAcessoQuebrado()
        )
        control.adicionar_responsavel_familiar(_dados_responsavel())

        with self.assertRaises(PersistenciaError):
            control.registrar_acesso("joao@email.com")

        self.assertEqual(control.listar_acessos(), [])


if __name__ == "__main__":
    unittest.main()
