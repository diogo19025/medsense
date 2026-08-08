import copy
import os
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collection.repositorio_perfil_saude import RepositorioPerfilSaude
from control.comando import Comando
from control.comandos_perfil_saude import (
    AtualizarPerfilSaudeCommand,
    CadastrarPerfilSaudeCommand,
    RemoverPerfilSaudeCommand,
)
from control.executor_comandos import ExecutorComandos
from control.facade_singleton_controller import FacadeSingletonController
from control.historico_perfil_saude import HistoricoPerfilSaude
from control.lembrete_control import LembreteControl
from control.perfil_saude_control import PerfilSaudeControl
from control.resumo_saude_builder import DiretorResumoSaude, ResumoSaudeTextoBuilder
from control.usuario_control import UsuarioControl
from entity.exceptions import PersistenciaError
from entity.perfil_saude import PerfilSaude


EMAIL_PACIENTE = "ana@email.com"
EMAIL_SEGUNDO_PACIENTE = "bruno@email.com"


def _perfil(**campos) -> PerfilSaude:
    dados = {
        "id": "perfil-1",
        "usuario_id": "usuario-1",
        "tipo_sanguineo": "O+",
        "alergias": ["Dipirona"],
        "condicoes_cronicas": ["Asma"],
        "medicamentos_continuos": ["Salbutamol"],
        "observacoes": "Acompanhamento semestral",
    }
    dados.update(campos)
    return PerfilSaude(**dados)


def _dados_perfil(**campos) -> dict:
    dados = {
        "tipo_sanguineo": "O+",
        "alergias": ["Dipirona"],
        "condicoes_cronicas": ["Asma"],
        "medicamentos_continuos": ["Salbutamol"],
        "observacoes": "Acompanhamento semestral",
    }
    dados.update(campos)
    return dados


def _usuario_control() -> UsuarioControl:
    control = UsuarioControl()
    control.adicionar_familiar_paciente(
        {
            "nome": "Ana Silva",
            "login": "ana",
            "email": EMAIL_PACIENTE,
            "senha": "SenhaForte1",
            "data_nascimento": "2000-01-01",
            "parentesco": "Filha",
        }
    )
    return control


class CommandPerfilSaudeTest(unittest.TestCase):
    def setUp(self):
        self.receiver = Mock(spec=PerfilSaudeControl)
        self.dados = _dados_perfil()

    def test_deve_executar_comando_de_cadastro_no_receiver(self):
        esperado = _perfil()
        self.receiver.cadastrar_perfil.return_value = esperado
        comando = CadastrarPerfilSaudeCommand(
            self.receiver, EMAIL_PACIENTE, self.dados
        )

        resultado = comando.executar()

        self.receiver.cadastrar_perfil.assert_called_once_with(
            EMAIL_PACIENTE, self.dados
        )
        self.assertIs(resultado, esperado)

    def test_deve_executar_comando_de_atualizacao_no_receiver(self):
        atual = _perfil()
        atualizado = _perfil(tipo_sanguineo="AB-")
        historico = HistoricoPerfilSaude()
        self.receiver.buscar_perfil.return_value = atual
        self.receiver.atualizar_perfil.return_value = atualizado
        comando = AtualizarPerfilSaudeCommand(
            self.receiver, historico, EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )

        resultado = comando.executar()

        self.receiver.atualizar_perfil.assert_called_once_with(
            EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )
        self.assertEqual(historico.recuperar(), atual.criar_memento())
        self.assertIs(resultado, atualizado)

    def test_deve_executar_comando_de_remocao_no_receiver(self):
        historico = HistoricoPerfilSaude()
        comando = RemoverPerfilSaudeCommand(
            self.receiver, historico, EMAIL_PACIENTE
        )

        comando.executar()

        self.receiver.remover_perfil.assert_called_once_with(EMAIL_PACIENTE)

    def test_remocao_deve_descartar_o_memento_do_perfil_removido(self):
        historico = HistoricoPerfilSaude()
        historico.salvar(_perfil().criar_memento())
        self.receiver.buscar_perfil.return_value = _perfil()
        comando = RemoverPerfilSaudeCommand(
            self.receiver, historico, EMAIL_PACIENTE
        )

        comando.executar()

        self.assertFalse(historico.possui_estado())

    def test_remocao_deve_preservar_o_memento_de_outro_perfil(self):
        historico = HistoricoPerfilSaude()
        memento_de_outro_paciente = _perfil().criar_memento()
        historico.salvar(memento_de_outro_paciente)
        self.receiver.buscar_perfil.return_value = _perfil(
            id="perfil-2", usuario_id="usuario-2"
        )
        comando = RemoverPerfilSaudeCommand(
            self.receiver, historico, "bruno@email.com"
        )

        comando.executar()

        self.assertEqual(historico.recuperar(), memento_de_outro_paciente)

    def test_executor_deve_acionar_o_comando_recebido(self):
        comando = Mock(spec=Comando)
        comando.executar.return_value = "resultado"

        resultado = ExecutorComandos().executar(comando)

        comando.executar.assert_called_once_with()
        self.assertEqual(resultado, "resultado")

    def test_nao_deve_salvar_memento_quando_atualizacao_falha(self):
        historico = HistoricoPerfilSaude()
        self.receiver.buscar_perfil.return_value = _perfil()
        self.receiver.atualizar_perfil.side_effect = PersistenciaError("falha")
        comando = AtualizarPerfilSaudeCommand(
            self.receiver, historico, EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )

        with self.assertRaises(PersistenciaError):
            comando.executar()

        self.assertFalse(historico.possui_estado())


class PerfilSaudeMementoTest(unittest.TestCase):
    def test_deve_criar_memento_com_todos_os_campos(self):
        perfil = _perfil()

        memento = perfil.criar_memento()

        self.assertEqual(memento.id, perfil.id)
        self.assertEqual(memento.usuario_id, perfil.usuario_id)
        self.assertEqual(memento.tipo_sanguineo, "O+")
        self.assertEqual(memento.alergias, ("Dipirona",))
        self.assertEqual(memento.condicoes_cronicas, ("Asma",))
        self.assertEqual(memento.medicamentos_continuos, ("Salbutamol",))
        self.assertEqual(memento.observacoes, "Acompanhamento semestral")

    def test_memento_deve_fazer_copias_defensivas_das_listas(self):
        perfil = _perfil()
        memento = perfil.criar_memento()

        perfil.alergias.append("Amendoim")
        perfil.condicoes_cronicas.clear()
        perfil.medicamentos_continuos.append("Corticoide")

        self.assertEqual(memento.alergias, ("Dipirona",))
        self.assertEqual(memento.condicoes_cronicas, ("Asma",))
        self.assertEqual(memento.medicamentos_continuos, ("Salbutamol",))

    def test_deve_restaurar_todos_os_campos_e_preservar_identidade(self):
        perfil = _perfil()
        memento = perfil.criar_memento()
        perfil.tipo_sanguineo = "AB-"
        perfil.alergias = []
        perfil.condicoes_cronicas = ["Diabetes"]
        perfil.medicamentos_continuos = []
        perfil.observacoes = "Alterada"

        perfil.restaurar(memento)

        self.assertEqual(perfil.id, "perfil-1")
        self.assertEqual(perfil.usuario_id, "usuario-1")
        self.assertEqual(perfil.tipo_sanguineo, "O+")
        self.assertEqual(perfil.alergias, ["Dipirona"])
        self.assertEqual(perfil.condicoes_cronicas, ["Asma"])
        self.assertEqual(perfil.medicamentos_continuos, ["Salbutamol"])
        self.assertEqual(perfil.observacoes, "Acompanhamento semestral")

    def test_restauracao_deve_criar_novas_listas(self):
        perfil = _perfil()
        memento = perfil.criar_memento()

        perfil.restaurar(memento)
        perfil.alergias.append("Amendoim")

        self.assertEqual(memento.alergias, ("Dipirona",))


class HistoricoPerfilSaudeTest(unittest.TestCase):
    def test_deve_manter_somente_o_ultimo_estado(self):
        historico = HistoricoPerfilSaude()
        primeiro = _perfil(tipo_sanguineo="O+").criar_memento()
        segundo = _perfil(tipo_sanguineo="AB-").criar_memento()

        historico.salvar(primeiro)
        historico.salvar(segundo)

        self.assertEqual(historico.recuperar(), segundo)

    def test_deve_lancar_erro_claro_quando_nao_ha_estado(self):
        with self.assertRaisesRegex(ValueError, "Nao existe atualizacao"):
            HistoricoPerfilSaude().recuperar()

    def test_deve_limpar_o_estado(self):
        historico = HistoricoPerfilSaude()
        historico.salvar(_perfil().criar_memento())

        historico.limpar()

        self.assertFalse(historico.possui_estado())


class RepositorioControlado(RepositorioPerfilSaude):
    def __init__(self):
        self._perfis = []
        self._gravacoes = 0
        self.falhar_na_gravacao = None

    def carregar(self):
        return copy.deepcopy(self._perfis)

    def salvar(self, perfis):
        self._gravacoes += 1
        if self._gravacoes == self.falhar_na_gravacao:
            raise PersistenciaError("falha simulada")
        self._perfis = copy.deepcopy(perfis)


class DesfazerAtualizacaoPerfilTest(unittest.TestCase):
    def setUp(self):
        FacadeSingletonController.resetar_instancia()
        self.repositorio = RepositorioControlado()
        self.usuario_control = _usuario_control()
        self.perfil_control = PerfilSaudeControl(
            self.usuario_control, self.repositorio
        )
        self.lembrete_control = LembreteControl(self.usuario_control)
        self.diretor_resumo_saude = DiretorResumoSaude(ResumoSaudeTextoBuilder())
        self.facade = FacadeSingletonController.obter_instancia(
            self.usuario_control,
            self.perfil_control,
            self.lembrete_control,
            self.diretor_resumo_saude,
        )
        self.original = self.facade.cadastrar_perfil_saude(
            EMAIL_PACIENTE, _dados_perfil()
        )

    def tearDown(self):
        FacadeSingletonController.resetar_instancia()

    # Cadastra um segundo paciente, com perfil, para os cenários em que o
    # Caretaker precisa distinguir de quem é o retrato guardado.
    def _cadastrar_segundo_paciente(self) -> None:
        self.usuario_control.adicionar_familiar_paciente(
            {
                "nome": "Bruno Souza",
                "login": "bruno",
                "email": EMAIL_SEGUNDO_PACIENTE,
                "senha": "SenhaForte1",
                "data_nascimento": "1995-05-05",
                "parentesco": "Filho",
            }
        )
        self.facade.cadastrar_perfil_saude(
            EMAIL_SEGUNDO_PACIENTE, _dados_perfil(tipo_sanguineo="A+")
        )

    def test_deve_desfazer_ultima_atualizacao_e_restaurar_todos_os_campos(self):
        id_original = self.original.id
        usuario_id_original = self.original.usuario_id
        self.facade.atualizar_perfil_saude(
            EMAIL_PACIENTE,
            _dados_perfil(
                tipo_sanguineo="AB-",
                alergias=[],
                condicoes_cronicas=["Diabetes"],
                medicamentos_continuos=["Insulina"],
                observacoes="Estado alterado",
            ),
        )

        restaurado = self.facade.desfazer_ultima_atualizacao_perfil()

        self.assertEqual(restaurado.id, id_original)
        self.assertEqual(restaurado.usuario_id, usuario_id_original)
        self.assertEqual(restaurado.tipo_sanguineo, "O+")
        self.assertEqual(restaurado.alergias, ["Dipirona"])
        self.assertEqual(restaurado.condicoes_cronicas, ["Asma"])
        self.assertEqual(restaurado.medicamentos_continuos, ["Salbutamol"])
        self.assertEqual(restaurado.observacoes, "Acompanhamento semestral")

    def test_desfazer_deve_restaurar_apenas_a_atualizacao_mais_recente(self):
        self.facade.atualizar_perfil_saude(
            EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )
        self.facade.atualizar_perfil_saude(
            EMAIL_PACIENTE, {"tipo_sanguineo": "A+"}
        )

        restaurado = self.facade.desfazer_ultima_atualizacao_perfil()

        self.assertEqual(restaurado.tipo_sanguineo, "AB-")

    def test_deve_limpar_historico_depois_de_desfazer(self):
        self.facade.atualizar_perfil_saude(
            EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )
        self.facade.desfazer_ultima_atualizacao_perfil()

        with self.assertRaisesRegex(ValueError, "Nao existe atualizacao"):
            self.facade.desfazer_ultima_atualizacao_perfil()

    def test_remover_o_proprio_perfil_deve_liberar_o_desfazer(self):
        self.facade.atualizar_perfil_saude(
            EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )
        self.facade.remover_perfil_saude(EMAIL_PACIENTE)
        self.facade.cadastrar_perfil_saude(EMAIL_PACIENTE, _dados_perfil())

        with self.assertRaisesRegex(ValueError, "Nao existe atualizacao"):
            self.facade.desfazer_ultima_atualizacao_perfil()

    def test_remover_perfil_de_outro_paciente_deve_preservar_o_desfazer(self):
        self._cadastrar_segundo_paciente()
        self.facade.atualizar_perfil_saude(
            EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )

        self.facade.remover_perfil_saude(EMAIL_SEGUNDO_PACIENTE)

        restaurado = self.facade.desfazer_ultima_atualizacao_perfil()
        self.assertEqual(restaurado.tipo_sanguineo, "O+")

    def test_deve_persistir_o_estado_restaurado(self):
        self.facade.atualizar_perfil_saude(
            EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )

        self.facade.desfazer_ultima_atualizacao_perfil()

        (persistido,) = self.repositorio.carregar()
        self.assertEqual(persistido.tipo_sanguineo, "O+")
        self.assertEqual(persistido.alergias, ["Dipirona"])

    def test_deve_preservar_ram_repositorio_e_historico_quando_desfazer_falha(self):
        self.facade.atualizar_perfil_saude(
            EMAIL_PACIENTE, {"tipo_sanguineo": "AB-"}
        )
        self.repositorio.falhar_na_gravacao = 3

        with self.assertRaises(PersistenciaError):
            self.facade.desfazer_ultima_atualizacao_perfil()

        em_ram = self.facade.buscar_perfil_saude(EMAIL_PACIENTE)
        (persistido,) = self.repositorio.carregar()
        self.assertEqual(em_ram.tipo_sanguineo, "AB-")
        self.assertEqual(persistido.tipo_sanguineo, "AB-")

        self.repositorio.falhar_na_gravacao = None
        restaurado = self.facade.desfazer_ultima_atualizacao_perfil()
        self.assertEqual(restaurado.tipo_sanguineo, "O+")


if __name__ == "__main__":
    unittest.main()
