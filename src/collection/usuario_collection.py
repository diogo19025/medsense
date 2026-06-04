from entity.usuario import Usuario


class UsuarioCollection:
    """Coleção em memória para persistência de usuários.

    Armazena instâncias de Usuario numa lista, simulando
    um repositório de dados em memória RAM.
    """

    def __init__(self):
        self._usuarios: list[Usuario] = []

    # Adiciona um novo usuário à coleção.
    # Lança ValueError se já existir um usuário com o mesmo email.
    def adicionar(self, usuario: Usuario) -> None:
        if self.buscar_por_email(usuario.email) is not None:
            raise ValueError(f"Já existe um usuário com o email '{usuario.email}'.")
        self._usuarios.append(usuario)

    # Retorna uma cópia da lista com todos os usuários cadastrados.
    def listar_todos(self) -> list[Usuario]:
        return list(self._usuarios)

    # Busca um usuário pelo email. Retorna None se não encontrado.
    def buscar_por_email(self, email: str) -> Usuario | None:
        for usuario in self._usuarios:
            if usuario.email == email:
                return usuario
        return None

    # Retorna a quantidade total de usuários na coleção.
    def quantidade(self) -> int:
        return len(self._usuarios)
