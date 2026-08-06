from control.comandos_perfil_saude import (
    AtualizarPerfilSaudeCommand,
    CadastrarPerfilSaudeCommand,
    RemoverPerfilSaudeCommand,
)
from control.executor_comandos import ExecutorComandos
from control.perfil_saude_control import PerfilSaudeControl
from control.usuario_control import UsuarioControl
from entity.perfil_saude import PerfilSaude
from entity.registro_acesso import RegistroAcesso
from entity.usuario import Usuario


class FacadeSingletonController:
    """
    Fachada única (padrão Facade + Singleton) para as operações de
    usuários e perfis de saúde.

    Esconde a existência de dois controllers separados (UsuarioControl e
    PerfilSaudeControl) atrás de uma interface só, simplificando o uso
    pela camada de boundary. Existe no máximo uma instância durante toda
    a execução do sistema: a primeira chamada a `obter_instancia` cria a
    fachada, as chamadas seguintes reaproveitam a mesma instância.
    """

    _instancia: "FacadeSingletonController | None" = None

    def __init__(
        self,
        usuario_control: UsuarioControl,
        perfil_saude_control: PerfilSaudeControl,
    ):
        self._usuario_control = usuario_control
        self._perfil_saude_control = perfil_saude_control
        self._executor_comandos = ExecutorComandos()

    # Devolve a única instância da fachada, criando-a na primeira chamada.
    # Chamadas seguintes ignoram os argumentos e reaproveitam a instância
    # já criada.
    @classmethod
    def obter_instancia(
        cls,
        usuario_control: UsuarioControl | None = None,
        perfil_saude_control: PerfilSaudeControl | None = None,
    ) -> "FacadeSingletonController":
        if cls._instancia is None:
            if usuario_control is None or perfil_saude_control is None:
                raise ValueError(
                    "A primeira chamada a obter_instancia precisa informar "
                    "usuario_control e perfil_saude_control."
                )
            cls._instancia = cls(usuario_control, perfil_saude_control)
        return cls._instancia

    # Descarta a instância única. Existe só para isolar os testes entre
    # si (cada teste começa com a fachada "zerada").
    @classmethod
    def resetar_instancia(cls) -> None:
        cls._instancia = None

    # ----- Usuários (delega para UsuarioControl) -----

    def validar_login(self, login: str) -> None:
        self._usuario_control.validar_login(login)

    def validar_senha(
        self, senha: str, login: str, nome: str = "", email: str = ""
    ) -> None:
        self._usuario_control.validar_senha(senha, login, nome, email)

    def adicionar_familiar_paciente(self, dados: dict) -> None:
        self._usuario_control.adicionar_familiar_paciente(dados)

    def adicionar_responsavel_familiar(self, dados: dict) -> None:
        self._usuario_control.adicionar_responsavel_familiar(dados)

    def listar_usuarios(self) -> list[Usuario]:
        return self._usuario_control.listar_usuarios()

    def buscar_usuario_por_email(self, email: str) -> Usuario | None:
        return self._usuario_control.buscar_usuario_por_email(email)

    def registrar_acesso(self, email: str, acao: str = "LOGIN") -> RegistroAcesso:
        return self._usuario_control.registrar_acesso(email, acao)

    def listar_acessos(self) -> list[RegistroAcesso]:
        return self._usuario_control.listar_acessos()

    def gerar_relatorio_acessos(self, formato: str) -> str:
        return self._usuario_control.gerar_relatorio_acessos(formato)

    # ----- Perfis de saúde (delega para PerfilSaudeControl) -----

    def cadastrar_perfil_saude(self, email: str, dados: dict) -> PerfilSaude:
        comando = CadastrarPerfilSaudeCommand(
            self._perfil_saude_control, email, dados
        )
        return self._executor_comandos.executar(comando)

    def buscar_perfil_saude(self, email: str) -> PerfilSaude | None:
        return self._perfil_saude_control.buscar_perfil(email)

    def listar_perfis_saude(self) -> list[PerfilSaude]:
        return self._perfil_saude_control.listar_perfis()

    def atualizar_perfil_saude(self, email: str, dados: dict) -> PerfilSaude:
        comando = AtualizarPerfilSaudeCommand(
            self._perfil_saude_control, email, dados
        )
        return self._executor_comandos.executar(comando)

    def remover_perfil_saude(self, email: str) -> None:
        comando = RemoverPerfilSaudeCommand(self._perfil_saude_control, email)
        self._executor_comandos.executar(comando)

    # ----- Consulta agregada -----

    # Soma usuários e perfis de saúde cadastrados no sistema.
    def quantidade_total_entidades(self) -> int:
        total_usuarios = len(self._usuario_control.listar_usuarios())
        total_perfis = len(self._perfil_saude_control.listar_perfis())
        return total_usuarios + total_perfis
