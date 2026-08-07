from boundary.perfil_saude_view import PerfilSaudeView
from boundary.usuario_view import UsuarioView
from control.facade_singleton_controller import FacadeSingletonController
from control.lembrete_control import LembreteControl
from control.observadores_lembrete import (
    NotificadorConsole,
    RegistroNotificacaoObserver,
)
from control.perfil_saude_control import PerfilSaudeControl
from control.resumo_saude_builder import DiretorResumoSaude, ResumoSaudeTextoBuilder
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
        usuario_control = UsuarioControl(
            repositorio=fabrica.criar_repositorio_usuarios(),
            logger=logger,
            repositorio_acessos=fabrica.criar_repositorio_acessos(),
        )
        perfil_control = PerfilSaudeControl(
            usuario_control=usuario_control,
            repositorio=fabrica.criar_repositorio_perfis_saude(),
            logger=logger,
        )
    except PersistenciaError as erro:
        print(f"Erro ao inicializar o armazenamento: {erro}")
        return

    lembrete_control = LembreteControl(usuario_control, logger=logger)
    lembrete_control.anexar_observador(NotificadorConsole())
    lembrete_control.anexar_observador(RegistroNotificacaoObserver(logger))

    # O diretor começa com o builder de texto; a facade permite trocar
    # para HTML sob demanda (definir_formato_resumo_saude), sem que a
    # camada de boundary precise conhecer as classes concretas.
    diretor_resumo_saude = DiretorResumoSaude(ResumoSaudeTextoBuilder())

    facade = FacadeSingletonController.obter_instancia(
        usuario_control,
        perfil_control,
        lembrete_control,
        diretor_resumo_saude,
    )

    view = UsuarioView(facade, PerfilSaudeView(facade))
    view.exibir_menu()


if __name__ == "__main__":
    main()