from control.comandos_perfil_saude import (
    AtualizarPerfilSaudeCommand,
    CadastrarPerfilSaudeCommand,
    RemoverPerfilSaudeCommand,
)
from control.executor_comandos import ExecutorComandos
from control.historico_perfil_saude import HistoricoPerfilSaude
from control.lembrete_control import LembreteControl
from control.perfil_saude_control import PerfilSaudeControl
from control.resumo_saude_builder import DiretorResumoSaude
from control.usuario_control import UsuarioControl
from entity.lembrete_saude import LembreteSaude
from entity.perfil_saude import PerfilSaude
from entity.registro_acesso import RegistroAcesso
from entity.resumo_saude import ResumoSaude
from entity.usuario import Usuario


class FacadeSingletonController:
    """
    Fachada única (padrão Facade + Singleton) para as operações de
    usuários, perfis de saúde, lembretes e resumos de saúde.

    Esconde a existência de controllers separados (UsuarioControl,
    PerfilSaudeControl, LembreteControl) e do diretor de resumos
    (DiretorResumoSaude) atrás de uma interface só, simplificando o uso
    pela camada de boundary. Existe no máximo uma instância durante toda
    a execução do sistema: a primeira chamada a `obter_instancia` cria a
    fachada, as chamadas seguintes reaproveitam a mesma instância.
    """

    _instancia: "FacadeSingletonController | None" = None

    def __init__(
        self,
        usuario_control: UsuarioControl,
        perfil_saude_control: PerfilSaudeControl,
        lembrete_control: LembreteControl,
        diretor_resumo_saude: DiretorResumoSaude,
    ):
        self._usuario_control = usuario_control
        self._perfil_saude_control = perfil_saude_control
        self._lembrete_control = lembrete_control
        self._diretor_resumo_saude = diretor_resumo_saude
        self._executor_comandos = ExecutorComandos()
        self._historico_perfil_saude = HistoricoPerfilSaude()

    # Devolve a única instância da fachada, criando-a na primeira chamada.
    # Chamadas seguintes ignoram os argumentos e reaproveitam a instância
    # já criada.
    @classmethod
    def obter_instancia(
        cls,
        usuario_control: UsuarioControl | None = None,
        perfil_saude_control: PerfilSaudeControl | None = None,
        lembrete_control: LembreteControl | None = None,
        diretor_resumo_saude: DiretorResumoSaude | None = None,
    ) -> "FacadeSingletonController":
        if cls._instancia is None:
            if (
                usuario_control is None
                or perfil_saude_control is None
                or lembrete_control is None
                or diretor_resumo_saude is None
            ):
                raise ValueError(
                    "A primeira chamada a obter_instancia precisa informar "
                    "usuario_control, perfil_saude_control, lembrete_control "
                    "e diretor_resumo_saude."
                )
            cls._instancia = cls(
                usuario_control,
                perfil_saude_control,
                lembrete_control,
                diretor_resumo_saude,
            )
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

    # ----- Perfis de saúde (delega para PerfilSaudeControl, via Command) -----

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
            self._perfil_saude_control,
            self._historico_perfil_saude,
            email,
            dados,
        )
        return self._executor_comandos.executar(comando)

    def remover_perfil_saude(self, email: str) -> None:
        comando = RemoverPerfilSaudeCommand(
            self._perfil_saude_control, self._historico_perfil_saude, email
        )
        self._executor_comandos.executar(comando)

    # Desfaz somente a última atualização de perfil de saúde executada
    # (padrão Memento). Lança ValueError se não há nada a desfazer.
    def desfazer_ultima_atualizacao_perfil(self) -> PerfilSaude:
        memento = self._historico_perfil_saude.recuperar()
        perfil = self._perfil_saude_control.restaurar_perfil(memento)
        self._historico_perfil_saude.limpar()
        return perfil

    # ----- Lembretes (delega para LembreteControl, padrão Observer) -----

    def criar_lembrete(self, email: str, dados: dict) -> LembreteSaude:
        return self._lembrete_control.criar_lembrete(email, dados)

    def atualizar_lembrete(self, id_lembrete: str, dados: dict) -> LembreteSaude:
        return self._lembrete_control.atualizar_lembrete(id_lembrete, dados)

    def concluir_lembrete(self, id_lembrete: str) -> None:
        self._lembrete_control.concluir_lembrete(id_lembrete)

    def listar_lembretes(self) -> list[LembreteSaude]:
        return self._lembrete_control.listar_lembretes()

    def listar_lembretes_por_usuario(self, email: str) -> list[LembreteSaude]:
        return self._lembrete_control.listar_lembretes_por_usuario(email)

    # ----- Resumo de saúde (delega para DiretorResumoSaude, padrão Builder) -----

    # Gera um resumo básico (dados do usuário + perfil de saúde) no
    # formato atual do builder configurado no diretor.
    def gerar_resumo_saude_basico(self, email: str) -> ResumoSaude:
        usuario = self._exigir_usuario(email)
        perfil = self._perfil_saude_control.buscar_perfil(email)
        return self._diretor_resumo_saude.construir_resumo_basico(usuario, perfil)

    # Gera um resumo completo, com as seções opcionais informadas.
    def gerar_resumo_saude_completo(
        self,
        email: str,
        *,
        medicamentos: list[str] | None = None,
        vacinas: list[str] | None = None,
        consultas: list[str] | None = None,
        documentos: list[str] | None = None,
    ) -> ResumoSaude:
        usuario = self._exigir_usuario(email)
        perfil = self._perfil_saude_control.buscar_perfil(email)
        return self._diretor_resumo_saude.construir_resumo_completo(
            usuario,
            perfil,
            medicamentos=medicamentos,
            vacinas=vacinas,
            consultas=consultas,
            documentos=documentos,
        )

    # Troca o builder usado pelo diretor (ex.: texto <-> HTML), sem que
    # quem chama a fachada precise conhecer as classes concretas.
    def definir_formato_resumo_saude(self, builder) -> None:
        self._diretor_resumo_saude.builder = builder

    def _exigir_usuario(self, email: str) -> Usuario:
        usuario = self._usuario_control.buscar_usuario_por_email(email)
        if usuario is None:
            raise ValueError(f"Nao existe usuario com o email '{email}'.")
        return usuario

    # ----- Consulta agregada -----

    # Soma usuários, perfis de saúde e lembretes cadastrados no sistema.
    def quantidade_total_entidades(self) -> int:
        total_usuarios = len(self._usuario_control.listar_usuarios())
        total_perfis = len(self._perfil_saude_control.listar_perfis())
        total_lembretes = len(self._lembrete_control.listar_lembretes())
        return total_usuarios + total_perfis + total_lembretes