from collection.lembrete_collection import LembreteCollection
from control.observadores_lembrete import ObservadorLembrete
from control.usuario_control import UsuarioControl
from entity.lembrete_saude import LembreteSaude, TipoLembrete
from infra.logger import Logger, LoggerNulo


class LembreteControl:
    """
    Responsável por gerenciar as operações de CRUD de lembretes e atuar
    como Subject no padrão Observer.

    Ponte entre interface e armazenamento, boundary e collection.
    Notifica a lista de observadores inscritos sempre que um lembrete
    sofre uma mutação relevante (criação, atualização ou conclusão).
    """

    def __init__(
        self,
        usuario_control: UsuarioControl,
        logger: Logger | None = None,
    ):
        self._usuarios = usuario_control
        self._collection = LembreteCollection()
        self._observadores: list[ObservadorLembrete] = []
        self._logger = logger if logger is not None else LoggerNulo()


    # MÉTODOS DO PADRÃO OBSERVER

    # inscreve um observador para receber notificações de lembretes.
    def anexar_observador(self, observador: ObservadorLembrete) -> None:
        if observador not in self._observadores:
            self._observadores.append(observador)

    # remove a inscrição de um observador.
    def desanexar_observador(self, observador: ObservadorLembrete) -> None:
        if observador in self._observadores:
            self._observadores.remove(observador)

    # avisa todos os observadores inscritos sobre uma ação.
    # a falha de um observador é registrada e segue adiante: o ADR-0009
    # exige que as implementações sejam independentes entre si, e a mutação
    # do Subject já aconteceu — deixar a exceção subir devolveria erro ao
    # chamador com o lembrete já gravado na coleção.
    def _notificar_observadores(self, lembrete: LembreteSaude, acao: str) -> None:
        for observador in self._observadores:
            try:
                observador.notificar(lembrete, acao)
            except Exception as erro:
                self._logger.erro(
                    f"Falha ao notificar {type(observador).__name__} sobre o "
                    f"lembrete '{lembrete.id_lembrete}': {erro}"
                )


    # REGRAS DE NEGÓCIO DA CONTROLADORA

    # resolve o email para o dono do lembrete (mesmo espírito de PerfilSaude).
    # lança ValueError se o email não existe.
    def _buscar_usuario(self, email: str):
        usuario = self._usuarios.buscar_usuario_por_email(email)
        if usuario is None:
            raise ValueError(f"Nao existe usuario com o email '{email}'.")
        return usuario

    # cadastra um novo lembrete, salva na collection e notifica observadores.
    def criar_lembrete(self, email: str, dados: dict) -> LembreteSaude:
        usuario = self._buscar_usuario(email)
        
        lembrete = LembreteSaude(
            id_lembrete=dados["id_lembrete"],
            usuario_id=usuario.id,
            titulo=dados["titulo"],
            descricao=dados.get("descricao", ""),
            data_hora=dados["data_hora"],
            tipo=dados["tipo"]
        )
        self._collection.adicionar(lembrete)
        self._notificar_observadores(lembrete, "criado")
        self._logger.info(f"Lembrete criado para o usuario: {usuario.login}")
        return lembrete

    # busca o lembrete pelo id, exigindo que ele exista.
    def _exigir_lembrete(self, id_lembrete: str) -> LembreteSaude:
        lembrete = self._collection.buscar_por_id(id_lembrete)
        if lembrete is None:
            raise ValueError(f"O lembrete com ID '{id_lembrete}' não foi encontrado.")
        return lembrete

    # atualiza dados de um lembrete existente e notifica observadores.
    # lança ValueError se o lembrete não for encontrado.
    def atualizar_lembrete(self, id_lembrete: str, dados: dict) -> LembreteSaude:
        atual = self._exigir_lembrete(id_lembrete)

        novo = LembreteSaude(
            id_lembrete=atual.id_lembrete,
            usuario_id=atual.usuario_id,
            titulo=dados.get("titulo", atual.titulo),
            descricao=dados.get("descricao", atual.descricao),
            data_hora=dados.get("data_hora", atual.data_hora),
            tipo=dados.get("tipo", atual.tipo),
            situacao=atual.situacao
        )
        self._collection.atualizar(novo)
        self._notificar_observadores(novo, "atualizado")
        self._logger.info(f"Lembrete atualizado: {id_lembrete}")
        return novo

    # marca o status do lembrete como concluído e notifica observadores.
    # lança ValueError se o lembrete não for encontrado.
    def concluir_lembrete(self, id_lembrete: str) -> None:
        lembrete = self._exigir_lembrete(id_lembrete)
        lembrete.concluir()
        self._collection.atualizar(lembrete)
        self._notificar_observadores(lembrete, "concluído")
        self._logger.info(f"Lembrete concluido: {id_lembrete}")

    # retorna uma cópia da lista com todos os lembretes cadastrados.
    def listar_lembretes(self) -> list[LembreteSaude]:
        return self._collection.listar_todos()

    # retorna os lembretes do usuário identificado pelo email.
    # lança ValueError se o email não existe.
    def listar_lembretes_por_usuario(self, email: str) -> list[LembreteSaude]:
        usuario = self._buscar_usuario(email)
        return self._collection.listar_por_usuario(usuario.id)