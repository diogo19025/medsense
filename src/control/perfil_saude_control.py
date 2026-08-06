from collection.perfil_saude_collection import PerfilSaudeCollection
from collection.repositorio_perfil_saude import RepositorioPerfilSaude
from control.usuario_control import UsuarioControl
from entity.familiar_paciente import FamiliarPaciente
from entity.perfil_saude import PerfilSaude
from entity.perfil_saude_memento import PerfilSaudeMemento
from entity.usuario import Usuario
from infra.logger import Logger, LoggerNulo


class PerfilSaudeControl:
    """
    Responsável por gerenciar as operações de CRUD de perfis de saúde.
    Ponte entre interface e armazenamento, boundary e collection.

    Cada perfil pertence a exatamente um FamiliarPaciente (composição 1:1
    do diagrama de classes); o dono é resolvido pelo email através do
    UsuarioControl, no mesmo espírito de registrar_acesso.

    A coleção em RAM é o cache de trabalho. Quando um repositório durável
    é informado, ele é carregado para a RAM no início da execução e
    espelhado a cada mudança, com desfazer-em-falha (ADR-0002, decisão 5).
    """

    def __init__(
        self,
        usuario_control: UsuarioControl,
        repositorio: RepositorioPerfilSaude | None = None,
        logger: Logger | None = None,
    ):
        self._usuarios = usuario_control
        self._collection = PerfilSaudeCollection()
        self._repositorio = repositorio
        self._logger = logger if logger is not None else LoggerNulo()
        self._carregar_do_repositorio()

    # Chaveia o armazenamento durável para a RAM no início da execução.
    def _carregar_do_repositorio(self) -> None:
        if self._repositorio is not None:
            for perfil in self._repositorio.carregar():
                self._collection.adicionar(perfil)

    # Resolve o email para o FamiliarPaciente dono do perfil.
    # Lança ValueError se o email não existe ou não pertence a um paciente.
    def _buscar_paciente(self, email: str) -> Usuario:
        usuario = self._usuarios.buscar_usuario_por_email(email)
        if usuario is None:
            raise ValueError(f"Nao existe usuario com o email '{email}'.")
        if not isinstance(usuario, FamiliarPaciente):
            raise ValueError(
                "Apenas familiares pacientes possuem perfil de saude."
            )
        return usuario

    # Espelha a coleção no armazenamento durável, executando o desfazer em
    # RAM caso a persistência falhe (mantém os dois consistentes).
    def _espelhar_no_repositorio(self, desfazer, descricao: str) -> None:
        try:
            if self._repositorio is not None:
                self._repositorio.salvar(self._collection.listar_todos())
        except Exception as erro:
            desfazer()
            self._logger.erro(f"Falha ao persistir {descricao}: {erro}")
            raise

    # Cadastra o perfil de saúde do paciente identificado pelo email.
    # Lança ValueError se o paciente já possui um perfil.
    def cadastrar_perfil(self, email: str, dados: dict) -> PerfilSaude:
        paciente = self._buscar_paciente(email)
        perfil = PerfilSaude(
            usuario_id=paciente.id,
            tipo_sanguineo=dados["tipo_sanguineo"],
            alergias=dados.get("alergias", []),
            condicoes_cronicas=dados.get("condicoes_cronicas", []),
            medicamentos_continuos=dados.get("medicamentos_continuos", []),
            observacoes=dados.get("observacoes", ""),
        )
        self._collection.adicionar(perfil)
        self._espelhar_no_repositorio(
            lambda: self._collection.remover(perfil),
            f"perfil de saude de '{paciente.login}'",
        )
        self._logger.info(f"Perfil de saude cadastrado: {paciente.login}")
        return perfil

    # Busca o perfil do paciente pelo email. Retorna None se não há perfil.
    def buscar_perfil(self, email: str) -> PerfilSaude | None:
        paciente = self._buscar_paciente(email)
        return self._collection.buscar_por_usuario(paciente.id)

    # Retorna uma cópia da lista com todos os perfis cadastrados.
    def listar_perfis(self) -> list[PerfilSaude]:
        return self._collection.listar_todos()

    # Atualiza somente os campos informados em `dados`, preservando os
    # demais e o vínculo/id do perfil existente.
    # Lança ValueError se o paciente não possui perfil.
    def atualizar_perfil(self, email: str, dados: dict) -> PerfilSaude:
        paciente = self._buscar_paciente(email)
        atual = self._exigir_perfil(paciente)
        novo = PerfilSaude(
            usuario_id=atual.usuario_id,
            tipo_sanguineo=dados.get("tipo_sanguineo", atual.tipo_sanguineo),
            alergias=dados.get("alergias", atual.alergias),
            condicoes_cronicas=dados.get(
                "condicoes_cronicas", atual.condicoes_cronicas
            ),
            medicamentos_continuos=dados.get(
                "medicamentos_continuos", atual.medicamentos_continuos
            ),
            observacoes=dados.get("observacoes", atual.observacoes),
            id=atual.id,
        )
        self._collection.atualizar(novo)
        self._espelhar_no_repositorio(
            lambda: self._collection.atualizar(atual),
            f"perfil de saude de '{paciente.login}'",
        )
        self._logger.info(f"Perfil de saude atualizado: {paciente.login}")
        return novo

    # Remove o perfil do paciente identificado pelo email.
    # Lança ValueError se o paciente não possui perfil.
    def remover_perfil(self, email: str) -> None:
        paciente = self._buscar_paciente(email)
        perfil = self._exigir_perfil(paciente)
        self._collection.remover(perfil)
        self._espelhar_no_repositorio(
            lambda: self._collection.adicionar(perfil),
            f"perfil de saude de '{paciente.login}'",
        )
        self._logger.info(f"Perfil de saude removido: {paciente.login}")

    def restaurar_perfil(self, memento: PerfilSaudeMemento) -> PerfilSaude:
        """Restaura e persiste um estado anterior, com rollback em falha."""
        perfil = self._collection.buscar_por_usuario(memento.usuario_id)
        if perfil is None:
            raise ValueError(
                "O perfil de saude da ultima atualizacao nao existe mais."
            )
        estado_atual = perfil.criar_memento()
        perfil.restaurar(memento)
        self._espelhar_no_repositorio(
            lambda: perfil.restaurar(estado_atual),
            f"restauracao do perfil de saude '{perfil.id}'",
        )
        self._logger.info(f"Atualizacao de perfil desfeita: {perfil.id}")
        return perfil

    # Busca o perfil do paciente, exigindo que ele exista.
    def _exigir_perfil(self, paciente: Usuario) -> PerfilSaude:
        perfil = self._collection.buscar_por_usuario(paciente.id)
        if perfil is None:
            raise ValueError(
                f"O usuario '{paciente.email}' nao possui perfil de saude."
            )
        return perfil
