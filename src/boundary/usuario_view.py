from control.usuario_control import UsuarioControl
from entity.exceptions import PersistenciaError, ValidacaoError, SenhaInvalidaError, LoginInvalidoError


class UsuarioView:
    """
    Interface de linha de comando para gerenciamento de usuários.
    Responsável apenas por entrada e saída de dados.
    """

    def __init__(self, control: UsuarioControl | None = None):
        self._control = control if control is not None else UsuarioControl()

    def _coletar_dados_base(self) -> dict:
        """Coleta dados comuns a todos os tipos de usuário."""

        nome = input("Nome: ")

        while True:
            try:
                login = input("Login: ")
                self._control.validar_login(login)
                break
            except LoginInvalidoError as erro:
                print(erro)
        
        email = input("Email: ")

        while True:
            try:
                senha = input("Senha: ")
                self._control.validar_senha(senha, login, nome, email)
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

    def _registrar_acesso(self) -> None:
        print("\n--- Registrar Acesso ---")
        email = input("Email do usuário: ")
        try:
            registro = self._control.registrar_acesso(email)
            print(f"Acesso registrado para '{registro.login}'.")
        except ValueError as e:
            print(f"Erro: {e}")

    def _gerar_relatorio_acessos(self) -> None:
        print("\n--- Relatório de Acessos ---")
        print("  [1] Texto")
        print("  [2] HTML")
        escolha = input("Escolha o formato: ").strip()
        formato = "html" if escolha == "2" else "texto"
        conteudo = self._control.gerar_relatorio_acessos(formato)

        extensao = "html" if formato == "html" else "txt"
        caminho = f"relatorio_acessos.{extensao}"
        try:
            with open(caminho, "w", encoding="utf-8") as arquivo:
                arquivo.write(conteudo)
            print(f"Relatório gerado em '{caminho}'.")
        except OSError as e:
            print(f"Erro ao gravar o relatório: {e}")
        print(conteudo)

    def exibir_menu(self) -> None:
        """Exibe o menu principal e processa a escolha do usuário."""
        while True:
            print("\n===== MedSense - Gerenciamento de Usuários =====")
            print("  [1] Adicionar familiar paciente")
            print("  [2] Adicionar responsável familiar")
            print("  [3] Listar todos os usuários")
            print("  [4] Registrar acesso de usuário")
            print("  [5] Gerar relatório de acessos")
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
            elif escolha == "0":
                print("Encerrando o sistema.")
                break
            else:
                print("Opção inválida. Tente novamente.")