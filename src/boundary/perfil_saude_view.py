from boundary.entrada import ler_lista
from control.facade_singleton_controller import FacadeSingletonController
from entity.exceptions import PersistenciaError, ValidacaoError


class PerfilSaudeView:
    """
    Interface de linha de comando para gerenciamento de perfis de saúde.
    Responsável apenas por entrada e saída de dados.
    """

    def __init__(self, facade: FacadeSingletonController):
        self._facade = facade

    def _coletar_dados(self) -> dict:
        return {
            "tipo_sanguineo": input("Tipo sanguíneo (ex.: O+, AB-): "),
            "alergias": ler_lista("Alergias"),
            "condicoes_cronicas": ler_lista("Condições crônicas"),
            "medicamentos_continuos": ler_lista("Medicamentos contínuos"),
            "observacoes": input("Observações: "),
        }

    def _cadastrar_perfil(self) -> None:
        print("\n--- Cadastro de Perfil de Saúde ---")
        email = input("Email do paciente: ")
        try:
            self._facade.cadastrar_perfil_saude(email, self._coletar_dados())
            print("Perfil de saúde cadastrado com sucesso!")
        except (ValidacaoError, ValueError) as e:
            print(f"Erro: {e}")
        except PersistenciaError as e:
            print(f"Erro de armazenamento: {e}")

    def _buscar_perfil(self) -> None:
        print("\n--- Buscar Perfil de Saúde ---")
        email = input("Email do paciente: ")
        try:
            perfil = self._facade.buscar_perfil_saude(email)
        except ValueError as e:
            print(f"Erro: {e}")
            return
        if perfil is None:
            print("O paciente ainda não possui perfil de saúde.")
            return
        print(perfil)

    def _listar_perfis(self) -> None:
        print("\n--- Lista de Perfis de Saúde ---")
        perfis = self._facade.listar_perfis_saude()
        if not perfis:
            print("Nenhum perfil de saúde cadastrado.")
            return
        for perfil in perfis:
            print(perfil)

    # Coleta apenas os campos que o usuário deseja mudar (vazio mantém).
    def _coletar_dados_atualizacao(self) -> dict:
        dados = {}
        tipo_sanguineo = input("Novo tipo sanguíneo (vazio para manter): ").strip()
        if tipo_sanguineo:
            dados["tipo_sanguineo"] = tipo_sanguineo
        if input("Atualizar alergias? [s/N]: ").strip().lower() == "s":
            dados["alergias"] = ler_lista("Alergias")
        if input("Atualizar condições crônicas? [s/N]: ").strip().lower() == "s":
            dados["condicoes_cronicas"] = ler_lista("Condições crônicas")
        if input("Atualizar medicamentos contínuos? [s/N]: ").strip().lower() == "s":
            dados["medicamentos_continuos"] = ler_lista("Medicamentos contínuos")
        if input("Atualizar observações? [s/N]: ").strip().lower() == "s":
            dados["observacoes"] = input("Observações: ")
        return dados

    def _atualizar_perfil(self) -> None:
        print("\n--- Atualizar Perfil de Saúde ---")
        email = input("Email do paciente: ")
        dados = self._coletar_dados_atualizacao()
        # Uma atualização sem campos não muda nada, mas guardaria um memento
        # e ocuparia a única vaga de desfazer com uma alteração inexistente.
        if not dados:
            print("Nenhum campo informado. O perfil de saúde não foi alterado.")
            return

        try:
            perfil = self._facade.atualizar_perfil_saude(email, dados)
            print("Perfil de saúde atualizado com sucesso!")
            print(perfil)
        except (ValidacaoError, ValueError) as e:
            print(f"Erro: {e}")
        except PersistenciaError as e:
            print(f"Erro de armazenamento: {e}")

    def _remover_perfil(self) -> None:
        print("\n--- Remover Perfil de Saúde ---")
        email = input("Email do paciente: ")
        try:
            self._facade.remover_perfil_saude(email)
            print("Perfil de saúde removido com sucesso!")
        except ValueError as e:
            print(f"Erro: {e}")
        except PersistenciaError as e:
            print(f"Erro de armazenamento: {e}")

    def exibir_menu(self) -> None:
        """Exibe o menu de perfis de saúde e processa a escolha do usuário."""
        while True:
            print("\n===== MedSense - Perfis de Saúde =====")
            print("  [1] Cadastrar perfil de saúde")
            print("  [2] Buscar perfil por paciente")
            print("  [3] Listar todos os perfis")
            print("  [4] Atualizar perfil de saúde")
            print("  [5] Remover perfil de saúde")
            print("  [0] Voltar ao menu principal")

            escolha = input("\nEscolha uma opção: ").strip()

            if escolha == "1":
                self._cadastrar_perfil()
            elif escolha == "2":
                self._buscar_perfil()
            elif escolha == "3":
                self._listar_perfis()
            elif escolha == "4":
                self._atualizar_perfil()
            elif escolha == "5":
                self._remover_perfil()
            elif escolha == "0":
                break
            else:
                print("Opção inválida. Tente novamente.")
