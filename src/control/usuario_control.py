from collection.usuario_collection import UsuarioCollection
from entity.familiar_paciente import FamiliarPaciente
from entity.responsavel_familiar import ResponsavelFamiliar
from entity.usuario import Usuario

class UsuarioControl:
    """
    Responsável por gerenciar as operaçõs de usuários.
    Ponte entre interface e armazenamento, boudary e collection    
    """

    def __init__(self):
        self._collection = UsuarioCollection()

    def listar_usuarios(self) -> list[Usuario]:
        # devolde explicitamente uma lista de usuários, mostrando na definição ao usar a função
        return self._collection.listar_todos()
    
    def adicionar_responsavel_familiar(self, dados: dict) -> None:
        """Cria um novo usuário familiar responsavel, 
        recebe um dicionario de dados empacota e adiciona,
        para boundary não ter que empacotar a classe, apenas receber o input de dados"""

        novo_usuario = ResponsavelFamiliar(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            parentesco_principal=dados["parentesco_principal"]
        )
        self._collection.adicionar(novo_usuario)

    def adicionar_familiar_paciente(self, dados: dict) -> None:
        """Cria um novo usuário familiar paciente, 
        recebe um dicionario de dados empacota e adiciona,
        para boundary não ter que empacotar a classe, apenas receber o input de dados"""

        novo_usuario = FamiliarPaciente(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            data_nascimento=dados["data_nascimento"],
            parentesco=dados["parentesco"]
        )
        self._collection.adicionar(novo_usuario)