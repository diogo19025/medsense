from uuid import uuid4

from control.facade_singleton_controller import FacadeSingletonController
from entity.exceptions import ValidacaoError
from entity.lembrete_saude import TipoLembrete


class LembreteView:
    """
    Interface de linha de comando para gerenciamento de lembretes de saúde.
    Responsável apenas por entrada e saída de dados.

    Fala com o sistema através da FacadeSingletonController, que delega
    para o LembreteControl (padrão Observer: os observadores são
    notificados a cada criação, atualização ou conclusão).
    """

    TIPOS = {
        "1": TipoLembrete.MEDICAMENTO,
        "2": TipoLembrete.CONSULTA,
        "3": TipoLembrete.EXAME,
        "4": TipoLembrete.OUTRO,
    }

    def __init__(self, facade: FacadeSingletonController):
        self._facade = facade

    def _escolher_tipo(self) -> TipoLembrete:
        print("  [1] Medicamento")
        print("  [2] Consulta")
        print("  [3] Exame")
        print("  [4] Outro")
        escolha = input("Tipo do lembrete: ").strip()
        return self.TIPOS.get(escolha, TipoLembrete.OUTRO)

    def _criar_lembrete(self) -> None:
        print("\n--- Criar Lembrete ---")
        email = input("Email do paciente: ")
        titulo = input("Título: ")
        descricao = input("Descrição: ")
        data_hora = input("Data e hora (ex.: 10/07/2026 08:00): ")
        tipo = self._escolher_tipo()

        dados = {
            "id_lembrete": str(uuid4()),
            "titulo": titulo,
            "descricao": descricao,
            "data_hora": data_hora,
            "tipo": tipo,
        }
        try:
            lembrete = self._facade.criar_lembrete(email, dados)
            print(f"Lembrete criado com sucesso! ID: {lembrete.id_lembrete}")
        except (ValidacaoError, ValueError) as e:
            print(f"Erro: {e}")

    def _atualizar_lembrete(self) -> None:
        print("\n--- Atualizar Lembrete ---")
        id_lembrete = input("ID do lembrete: ")
        dados = {}
        titulo = input("Novo título (vazio para manter): ").strip()
        if titulo:
            dados["titulo"] = titulo
        descricao = input("Nova descrição (vazio para manter): ").strip()
        if descricao:
            dados["descricao"] = descricao
        data_hora = input("Nova data e hora (vazio para manter): ").strip()
        if data_hora:
            dados["data_hora"] = data_hora
        if input("Alterar tipo? [s/N]: ").strip().lower() == "s":
            dados["tipo"] = self._escolher_tipo()

        try:
            self._facade.atualizar_lembrete(id_lembrete, dados)
            print("Lembrete atualizado com sucesso!")
        except (ValidacaoError, ValueError) as e:
            print(f"Erro: {e}")

    def _concluir_lembrete(self) -> None:
        print("\n--- Concluir Lembrete ---")
        id_lembrete = input("ID do lembrete: ")
        try:
            self._facade.concluir_lembrete(id_lembrete)
            print("Lembrete marcado como concluído!")
        except ValueError as e:
            print(f"Erro: {e}")

    def _listar_lembretes(self) -> None:
        print("\n--- Lista de Lembretes ---")
        lembretes = self._facade.listar_lembretes()
        if not lembretes:
            print("Nenhum lembrete cadastrado.")
            return
        for lembrete in lembretes:
            print(
                f"[{lembrete.id_lembrete[:8]}...] {lembrete.titulo} | "
                f"Tipo: {lembrete.tipo.value} | "
                f"Situação: {lembrete.situacao.value} | "
                f"Data: {lembrete.data_hora}"
            )

    def exibir_menu(self) -> None:
        """Exibe o menu de lembretes e processa a escolha do usuário."""
        while True:
            print("\n===== MedSense - Lembretes de Saúde =====")
            print("  [1] Criar lembrete")
            print("  [2] Atualizar lembrete")
            print("  [3] Concluir lembrete")
            print("  [4] Listar todos os lembretes")
            print("  [0] Voltar ao menu principal")

            escolha = input("\nEscolha uma opção: ").strip()

            if escolha == "1":
                self._criar_lembrete()
            elif escolha == "2":
                self._atualizar_lembrete()
            elif escolha == "3":
                self._concluir_lembrete()
            elif escolha == "4":
                self._listar_lembretes()
            elif escolha == "0":
                break
            else:
                print("Opção inválida. Tente novamente.")