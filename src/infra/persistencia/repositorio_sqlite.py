import json
import sqlite3
from datetime import datetime

from collection.repositorio_acesso import RepositorioAcesso
from collection.repositorio_perfil_saude import RepositorioPerfilSaude
from collection.repositorio_usuario import RepositorioUsuario
from entity.exceptions import BancoDadosError
from entity.familiar_paciente import FamiliarPaciente
from entity.perfil_saude import PerfilSaude
from entity.registro_acesso import RegistroAcesso
from entity.responsavel_familiar import ResponsavelFamiliar
from entity.usuario import Usuario

BANCO_PADRAO = "usuarios.db"


class RepositorioSQLite(RepositorioUsuario):
    """Persistência de usuários em banco de dados SQLite.

    Toda operação de banco é envolvida em tratamento de exceções:
    sqlite3.Error (análogo a SQLException) é convertida em BancoDadosError
    para a camada de aplicação.
    """

    def __init__(self, caminho: str = BANCO_PADRAO):
        self._caminho = str(caminho)
        self._criar_tabela()

    def _conectar(self) -> sqlite3.Connection:
        return sqlite3.connect(self._caminho)

    # Garante que a tabela exista antes de qualquer leitura ou escrita.
    def _criar_tabela(self) -> None:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id TEXT PRIMARY KEY,
                    tipo TEXT NOT NULL,
                    nome TEXT NOT NULL,
                    login TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    senha TEXT NOT NULL,
                    data_nascimento TEXT,
                    parentesco TEXT,
                    parentesco_principal TEXT
                )
                """
            )
            conexao.commit()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao preparar a tabela de usuários: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()

    # Lê todos os usuários do banco e os reconstrói nas subclasses corretas.
    def carregar(self) -> list[Usuario]:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.row_factory = sqlite3.Row
            linhas = conexao.execute("SELECT * FROM usuarios").fetchall()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao carregar usuários do banco: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()
        return [self._reconstruir(linha) for linha in linhas]

    # Reescreve toda a coleção: limpa a tabela e insere os usuários atuais.
    def salvar(self, usuarios: list[Usuario]) -> None:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.execute("DELETE FROM usuarios")
            conexao.executemany(
                """
                INSERT INTO usuarios
                    (id, tipo, nome, login, email, senha,
                     data_nascimento, parentesco, parentesco_principal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [self._para_linha(usuario) for usuario in usuarios],
            )
            conexao.commit()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao salvar usuários no banco: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()

    # Achata um usuário em uma linha da tabela (campos ausentes viram None).
    @staticmethod
    def _para_linha(usuario: Usuario) -> tuple:
        return (
            usuario.id,
            usuario.tipo_usuario,
            usuario.nome,
            usuario.login,
            usuario.email,
            usuario.senha,
            getattr(usuario, "data_nascimento", None),
            getattr(usuario, "parentesco", None),
            getattr(usuario, "parentesco_principal", None),
        )

    # Recria a subclasse de Usuario a partir do tipo armazenado.
    @staticmethod
    def _reconstruir(linha: sqlite3.Row) -> Usuario:
        tipo = linha["tipo"]
        if tipo == "FAMILIAR_PACIENTE":
            return FamiliarPaciente(
                id=linha["id"],
                nome=linha["nome"],
                login=linha["login"],
                email=linha["email"],
                senha=linha["senha"],
                data_nascimento=linha["data_nascimento"] or "",
                parentesco=linha["parentesco"] or "",
            )
        if tipo == "RESPONSAVEL_FAMILIAR":
            return ResponsavelFamiliar(
                id=linha["id"],
                nome=linha["nome"],
                login=linha["login"],
                email=linha["email"],
                senha=linha["senha"],
                parentesco_principal=linha["parentesco_principal"] or "",
            )
        raise BancoDadosError(f"Tipo de usuário desconhecido no banco: '{tipo}'")


class RepositorioAcessoSQLite(RepositorioAcesso):
    """Persistência de registros de acesso em banco de dados SQLite.

    Compartilha o mesmo arquivo de banco do RepositorioSQLite (tabela
    própria `acessos`), formando com ele a família SQLite de repositórios.
    """

    def __init__(self, caminho: str = BANCO_PADRAO):
        self._caminho = str(caminho)
        self._criar_tabela()

    def _conectar(self) -> sqlite3.Connection:
        return sqlite3.connect(self._caminho)

    # Garante que a tabela exista antes de qualquer leitura ou escrita.
    def _criar_tabela(self) -> None:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS acessos (
                    usuario_id TEXT NOT NULL,
                    login TEXT NOT NULL,
                    tipo_usuario TEXT NOT NULL,
                    acao TEXT NOT NULL,
                    momento TEXT NOT NULL
                )
                """
            )
            conexao.commit()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao preparar a tabela de acessos: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()

    # Lê todos os registros de acesso do banco, na ordem de inserção.
    def carregar(self) -> list[RegistroAcesso]:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.row_factory = sqlite3.Row
            linhas = conexao.execute("SELECT * FROM acessos").fetchall()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao carregar acessos do banco: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()
        return [self._reconstruir(linha) for linha in linhas]

    # Reescreve toda a coleção: limpa a tabela e insere os registros atuais.
    def salvar(self, registros: list[RegistroAcesso]) -> None:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.execute("DELETE FROM acessos")
            conexao.executemany(
                """
                INSERT INTO acessos
                    (usuario_id, login, tipo_usuario, acao, momento)
                VALUES (?, ?, ?, ?, ?)
                """,
                [self._para_linha(registro) for registro in registros],
            )
            conexao.commit()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao salvar acessos no banco: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()

    # Achata um registro em uma linha da tabela (momento em ISO 8601).
    @staticmethod
    def _para_linha(registro: RegistroAcesso) -> tuple:
        return (
            registro.usuario_id,
            registro.login,
            registro.tipo_usuario,
            registro.acao,
            registro.momento.isoformat(),
        )

    # Recria o registro de acesso a partir de uma linha da tabela.
    @staticmethod
    def _reconstruir(linha: sqlite3.Row) -> RegistroAcesso:
        return RegistroAcesso(
            usuario_id=linha["usuario_id"],
            login=linha["login"],
            tipo_usuario=linha["tipo_usuario"],
            acao=linha["acao"],
            momento=datetime.fromisoformat(linha["momento"]),
        )


class RepositorioPerfilSaudeSQLite(RepositorioPerfilSaude):
    """Persistência de perfis de saúde em banco de dados SQLite.

    Compartilha o mesmo arquivo de banco do RepositorioSQLite (tabela
    própria `perfis_saude`), formando com ele a família SQLite de
    repositórios. As listas (alergias, condições, medicamentos) são
    serializadas em JSON, pois SQLite não possui tipo de coluna de lista.
    """

    def __init__(self, caminho: str = BANCO_PADRAO):
        self._caminho = str(caminho)
        self._criar_tabela()

    def _conectar(self) -> sqlite3.Connection:
        return sqlite3.connect(self._caminho)

    # Garante que a tabela exista antes de qualquer leitura ou escrita.
    def _criar_tabela(self) -> None:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.execute(
                """
                CREATE TABLE IF NOT EXISTS perfis_saude (
                    id TEXT PRIMARY KEY,
                    usuario_id TEXT NOT NULL UNIQUE,
                    tipo_sanguineo TEXT NOT NULL,
                    alergias TEXT NOT NULL,
                    condicoes_cronicas TEXT NOT NULL,
                    medicamentos_continuos TEXT NOT NULL,
                    observacoes TEXT NOT NULL
                )
                """
            )
            conexao.commit()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao preparar a tabela de perfis de saúde: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()

    # Lê todos os perfis de saúde do banco.
    def carregar(self) -> list[PerfilSaude]:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.row_factory = sqlite3.Row
            linhas = conexao.execute("SELECT * FROM perfis_saude").fetchall()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao carregar perfis de saúde do banco: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()
        return [self._reconstruir(linha) for linha in linhas]

    # Reescreve toda a coleção: limpa a tabela e insere os perfis atuais.
    def salvar(self, perfis: list[PerfilSaude]) -> None:
        conexao = None
        try:
            conexao = self._conectar()
            conexao.execute("DELETE FROM perfis_saude")
            conexao.executemany(
                """
                INSERT INTO perfis_saude
                    (id, usuario_id, tipo_sanguineo, alergias,
                     condicoes_cronicas, medicamentos_continuos, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [self._para_linha(perfil) for perfil in perfis],
            )
            conexao.commit()
        except sqlite3.Error as erro:
            raise BancoDadosError(
                f"Falha ao salvar perfis de saúde no banco: {erro}"
            ) from erro
        finally:
            if conexao is not None:
                conexao.close()

    # Achata um perfil em uma linha da tabela (listas em JSON).
    @staticmethod
    def _para_linha(perfil: PerfilSaude) -> tuple:
        return (
            perfil.id,
            perfil.usuario_id,
            perfil.tipo_sanguineo,
            json.dumps(perfil.alergias),
            json.dumps(perfil.condicoes_cronicas),
            json.dumps(perfil.medicamentos_continuos),
            perfil.observacoes,
        )

    # Recria o perfil de saúde a partir de uma linha da tabela.
    @staticmethod
    def _reconstruir(linha: sqlite3.Row) -> PerfilSaude:
        return PerfilSaude(
            id=linha["id"],
            usuario_id=linha["usuario_id"],
            tipo_sanguineo=linha["tipo_sanguineo"],
            alergias=json.loads(linha["alergias"]),
            condicoes_cronicas=json.loads(linha["condicoes_cronicas"]),
            medicamentos_continuos=json.loads(linha["medicamentos_continuos"]),
            observacoes=linha["observacoes"],
        )
