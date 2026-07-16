from boundary.perfil_saude_view import PerfilSaudeView
from boundary.usuario_view import UsuarioView
from control.perfil_saude_control import PerfilSaudeControl
from control.usuario_control import UsuarioControl
from entity.exceptions import PersistenciaError
from infra.logging_adapter import LoggingAdapter
from infra.persistencia.fabrica_repositorios import FabricaRepositorios, criar_fabrica


# Permite chavear o mecanismo de armazenamento no início da execução:
# a fábrica escolhida produz a família completa de repositórios (Abstract
# Factory), um por entidade, sem expor as classes concretas às demais camadas.
def selecionar_fabrica() -> FabricaRepositorios:
    print("===== MedSense - Armazenamento =====")
    print("  [1] Memória (RAM)")
    print("  [2] Arquivo binário")
    print("  [3] Banco de dados (SQLite)")
    escolha = input("Escolha o mecanismo de armazenamento: ").strip()
    if escolha == "2":
        return criar_fabrica("arquivo")
    if escolha == "3":
        return criar_fabrica("sqlite")
    return criar_fabrica("memoria")


def main():
    try:
        fabrica = selecionar_fabrica()
        logger = LoggingAdapter()
        control = UsuarioControl(
            repositorio=fabrica.criar_repositorio_usuarios(),
            logger=logger,
            repositorio_acessos=fabrica.criar_repositorio_acessos(),
        )
        perfil_control = PerfilSaudeControl(
            usuario_control=control,
            repositorio=fabrica.criar_repositorio_perfis_saude(),
            logger=logger,
        )
    except PersistenciaError as erro:
        print(f"Erro ao inicializar o armazenamento: {erro}")
        return

    view = UsuarioView(control, PerfilSaudeView(perfil_control))
    view.exibir_menu()


if __name__ == "__main__":
    main()
