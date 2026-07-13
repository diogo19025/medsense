from collection.repositorio_usuario import RepositorioUsuario
from collection.usuario_collection import UsuarioCollection
from entity.familiar_paciente import FamiliarPaciente
from entity.responsavel_familiar import ResponsavelFamiliar
from entity.validador_usuario import ValidadorUsuario
from entity.usuario import Usuario
from infra.logger import Logger, LoggerNulo

class UsuarioControl:
    """
    Responsável por gerenciar as operaçõs de usuários.
    Ponte entre interface e armazenamento, boudary e collection

    A coleção em RAM é o cache de trabalho. Quando um repositório durável
    (arquivo binário ou banco de dados) é informado, ele é carregado para a
    RAM no início da execução e atualizado a cada novo cadastro.

    Depende da porta de log `Logger` (padrão Adapter) para registrar eventos,
    sem se acoplar a nenhuma biblioteca concreta de log.
    """

    def __init__(
        self,
        repositorio: RepositorioUsuario | None = None,
        logger: Logger | None = None,
    ):
        self._collection = UsuarioCollection()
        self._repositorio = repositorio
        self._logger = logger if logger is not None else LoggerNulo()
        self._carregar_do_repositorio()

    # Chaveia o armazenamento durável para a RAM no início da execução.
    def _carregar_do_repositorio(self) -> None:
        if self._repositorio is None:
            return
        for usuario in self._repositorio.carregar():
            self._collection.adicionar(usuario)

    # Adiciona à RAM e espelha no armazenamento durável, desfazendo a
    # adição em RAM caso a persistência falhe (mantém os dois consistentes).
    def _adicionar(self, novo_usuario: Usuario) -> None:
        self._collection.adicionar(novo_usuario)
        try:
            if self._repositorio is not None:
                self._repositorio.salvar(self._collection.listar_todos())
        except Exception as erro:
            self._collection.remover(novo_usuario)
            self._logger.erro(
                f"Falha ao persistir usuario '{novo_usuario.login}': {erro}"
            )
            raise
        self._logger.info(
            f"Usuario cadastrado: {novo_usuario.login} ({novo_usuario.tipo_usuario})"
        )

    def validar_senha(self, senha: str, login: str, nome:str = "", email: str = "") -> None:
        indentificadores = (login, nome, email)
        ValidadorUsuario.validar_senha(senha, indentificadores)

    def validar_login(self, login: str) -> None:
        ValidadorUsuario.validar_login(login)    

    def listar_usuarios(self) -> list[Usuario]:
        # devolde explicitamente uma lista de usuários, mostrando na definição ao usar a função
        return self._collection.listar_todos()

    def adicionar_responsavel_familiar(self, dados: dict) -> None:
        """Cria um novo usuário familiar responsavel,
        recebe um dicionario de dados empacota e adiciona,
        para boundary não ter que empacotar a classe, apenas receber o input de dados"""

        novo_usuario = ResponsavelFamiliar(
            nome=dados["nome"],
            login=dados["login"],
            email=dados["email"],
            senha=dados["senha"],
            parentesco_principal=dados["parentesco_principal"]
        )
        self._adicionar(novo_usuario)

    def adicionar_familiar_paciente(self, dados: dict) -> None:
        """Cria um novo usuário familiar paciente,
        recebe um dicionario de dados empacota e adiciona,
        para boundary não ter que empacotar a classe, apenas receber o input de dados"""

        novo_usuario = FamiliarPaciente(
            nome=dados["nome"],
            login=dados["login"],
            email=dados["email"],
            senha=dados["senha"],
            data_nascimento=dados["data_nascimento"],
            parentesco=dados["parentesco"]
        )
        self._adicionar(novo_usuario)