from boundary.usuario_view import UsuarioView
from collection.repositorio_arquivo import RepositorioArquivoBinario
from collection.repositorio_sqlite import RepositorioSQLite
from collection.repositorio_usuario import RepositorioUsuario
from control.usuario_control import UsuarioControl
from entity.exceptions import PersistenciaError


# Permite chavear o mecanismo de armazenamento no início da execução.
def selecionar_repositorio() -> RepositorioUsuario | None:
    print("===== MedSense - Armazenamento =====")
    print("  [1] Memória (RAM)")
    print("  [2] Arquivo binário")
    print("  [3] Banco de dados (SQLite)")
    escolha = input("Escolha o mecanismo de armazenamento: ").strip()
    if escolha == "2":
        return RepositorioArquivoBinario()
    if escolha == "3":
        return RepositorioSQLite()
    return None


def main():
    try:
        repositorio = selecionar_repositorio()
        control = UsuarioControl(repositorio)
    except PersistenciaError as erro:
        print(f"Erro ao inicializar o armazenamento: {erro}")
        return

    view = UsuarioView(control)
    view.exibir_menu()


if __name__ == "__main__":
    main()
