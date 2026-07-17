from boundary.perfil_saude_view import PerfilSaudeView
from control.facade_singleton_controller import FacadeSingletonController
from control.perfil_saude_control import PerfilSaudeControl
from control.usuario_control import UsuarioControl
from entity.exceptions import PersistenciaError, ValidacaoError, SenhaInvalidaError, LoginInvalidoError


class UsuarioView:
    """
    Interface de linha de comando para gerenciamento de usuários.
    Responsável apenas por entrada e saída de dados.

    Fala com o sistema através da FacadeSingletonController: não conhece
    UsuarioControl nem PerfilSaudeControl diretamente, apenas a fachada
    que os integra.
    """

    def __init__(
        self,
        facade: FacadeSingletonController | None = None,
        perfil_saude_view: PerfilSaudeView | None = None,
    ):
        if facade is not None:
            self._facade = facade
        else:
            usuario_control = UsuarioControl()
            perfil_control = PerfilSaudeControl(usuario_control)
            self._facade = FacadeSingletonController.obter_instancia(
                usuario_control, perfil_control
            )

        self._perfil_saude_view = (
            perfil_saude_view
            if perfil_saude_view is not None
            # A facade expõe buscar_usuario_por_email, então serve como
            # o "usuario_control" que o PerfilSaudeControl espera —
            # mantém os dois usando a mesma base de usuários.
            else PerfilSaudeView(PerfilSaudeControl(self._facade))
        )

    def _coletar_dados_base(self) -> dict:
        """Coleta dados comuns a todos os tipos de usuário."""

        nome = input("Nome: ")

        while True:
            try:
                login = input("Login: ")
                self._facade.validar_login(login)
                break
            except LoginInvalidoError as erro:
                print(erro)

        email = input("Email: ")

        while True:
            try:
                senha = input("Senha: ")
                self._facade.validar_senha(senha, login, nome, email)
                break
            except SenhaInvalidaError as erro:
                print(erro)

        return {
            "nome": nome,
            "login": login,
            "email": email,
            "senha": senha
        }

    def _adicionar_familiar_paciente(self) -> None:
        print("\n--- Cadastro de Familiar Paciente ---")
        dados = self._coletar_dados_base()
        dados["data_nascimento"] = input("Data de nascimento: ")
        dados["parentesco"] = input("Parentesco: ")
        try:
            self._facade.adicionar_familiar_paciente(dados)
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
            self._facade.adicionar_responsavel_familiar(dados)
            print("Responsável familiar cadastrado com sucesso!")
        except (ValidacaoError, ValueError) as e:
            print(f"Erro: {e}")
        except PersistenciaError as e:
            print(f"Erro de armazenamento: {e}")

    def _listar_usuarios(self) -> None:
        print("\n--- Lista de Usuários ---")
        usuarios = self._facade.listar_usuarios()
        if not usuarios:
            print("Nenhum usuário cadastrado.")
            return
        for usuario in usuarios:
            print(usuario)

    def _registrar_acesso(self) -> None:
        print("\n--- Registrar Acesso ---")
        email = input("Email do usuário: ")
        try:
            registro = self._facade.registrar_acesso(email)
            print(f"Acesso registrado para '{registro.login}'.")
        except ValueError as e:
            print(f"Erro: {e}")

    def _gerar_relatorio_acessos(self) -> None:
        print("\n--- Relatório de Acessos ---")
        print("  [1] Texto")
        print("  [2] HTML")
        escolha = input("Escolha o formato: ").strip()
        formato = "html" if escolha == "2" else "texto"
        conteudo = self._facade.gerar_relatorio_acessos(formato)

        extensao = "html" if formato == "html" else "txt"
        caminho = f"relatorio_acessos.{extensao}"
        try:
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write(conteudo)
            print(f"Relatório gerado em '{caminho}'.")
        except OSError as e:
            print(f"Erro ao gravar o relatório: {e}")
        print(conteudo)

    def _exibir_quantidade_total_entidades(self) -> None:
        print("\n--- Total de Entidades Cadastradas ---")
        total = self._facade.quantidade_total_entidades()
        print(f"Usuários + perfis de saúde cadastrados: {total}")

    def exibir_menu(self) -> None:
        """Exibe o menu principal e processa a escolha do usuário."""
        while True:
            print("\n===== MedSense - Gerenciamento de Usuários =====")
            print("  [1] Adicionar familiar paciente")
            print("  [2] Adicionar responsável familiar")
            print("  [3] Listar todos os usuários")
            print("  [4] Registrar acesso de usuário")
            print("  [5] Gerar relatório de acessos")
            print("  [6] Gerenciar perfis de saúde")
            print("  [7] Ver total de entidades cadastradas")
            print("  [0] Sair")

            escolha = input("\nEscolha uma opção: ").strip()

            if escolha == "1":
                self._adicionar_familiar_paciente()
            elif escolha == "2":
                self._adicionar_responsavel_familiar()
            elif escolha == "3":
                self._listar_usuarios()
            elif escolha == "4":
                self._registrar_acesso()
            elif escolha == "5":
                self._gerar_relatorio_acessos()
            elif escolha == "6":
                self._perfil_saude_view.exibir_menu()
            elif escolha == "7":
                self._exibir_quantidade_total_entidades()
            elif escolha == "0":
                print("Encerrando o sistema.")
                break
            else:
                print("Opção inválida. Tente novamente.")