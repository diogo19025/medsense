from control.usuario_control import UsuarioControl
from entity.exceptions import PersistenciaError, ValidacaoError


class UsuarioView:
    """
    Interface de linha de comando para gerenciamento de usuários.
    Responsável apenas por entrada e saída de dados.
    """

    def __init__(self, control: UsuarioControl | None = None):
        self._control = control if control is not None else UsuarioControl()

    def _coletar_dados_base(self) -> dict:
        """Coleta dados comuns a todos os tipos de usuário."""
        return {
            "nome": input("Nome: "),
            "login": input("Login: "),
            "email": input("Email: "),
            "senha": input("Senha: "),
        }

    def _adicionar_familiar_paciente(self) -> None:
        print("\n--- Cadastro de Familiar Paciente ---")
        dados = self._coletar_dados_base()
        dados["data_nascimento"] = input("Data de nascimento: ")
        dados["parentesco"] = input("Parentesco: ")
        try:
            self._control.adicionar_familiar_paciente(dados)
            print("Familiar paciente cadastrado com sucesso!")
        except (ValidacaoError, ValueError) as e:
            print(f"Erro: {e}")
        except PersistenciaError as e:
            print(f"Erro de armazenamento: {e}")

    def _adicionar_responsavel_familiar(self) -> None:
        print("\n--- Cadastro de Responsável Familiar ---")
        dados = self._coletar_dados_base()
        dados["parentesco_principal"] = input("Parentesco principal: ")
        try:
            self._control.adicionar_responsavel_familiar(dados)
            print("Responsável familiar cadastrado com sucesso!")
        except (ValidacaoError, ValueError) as e:
            print(f"Erro: {e}")
        except PersistenciaError as e:
            print(f"Erro de armazenamento: {e}")

    def _listar_usuarios(self) -> None:
        print("\n--- Lista de Usuários ---")
        usuarios = self._control.listar_usuarios()
        if not usuarios:
            print("Nenhum usuário cadastrado.")
            return
        for usuario in usuarios:
            print(usuario)

    def exibir_menu(self) -> None:
        """Exibe o menu principal e processa a escolha do usuário."""
        while True:
            print("\n===== MedSense - Gerenciamento de Usuários =====")
            print("  [1] Adicionar familiar paciente")
            print("  [2] Adicionar responsável familiar")
            print("  [3] Listar todos os usuários")
            print("  [0] Sair")

            escolha = input("\nEscolha uma opção: ").strip()

            if escolha == "1":
                self._adicionar_familiar_paciente()
            elif escolha == "2":
                self._adicionar_responsavel_familiar()
            elif escolha == "3":
                self._listar_usuarios()
            elif escolha == "0":
                print("Encerrando o sistema.")
                break
            else:
                print("Opção inválida. Tente novamente.")