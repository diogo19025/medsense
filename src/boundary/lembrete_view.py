from datetime import datetime
from uuid import uuid4

from control.facade_singleton_controller import FacadeSingletonController
from entity.exceptions import ValidacaoError
from entity.lembrete_saude import LembreteSaude, TipoLembrete


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

    @staticmethod
    def _converter_data_hora(valor: str) -> datetime:
        try:
            return datetime.strptime(valor.strip(), "%d/%m/%Y %H:%M")
        except ValueError as erro:
            raise ValueError(
                "Data e hora invalidas. Use o formato DD/MM/AAAA HH:MM."
            ) from erro

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

        try:
            dados = {
                "id_lembrete": str(uuid4()),
                "titulo": titulo,
                "descricao": descricao,
                "data_hora": self._converter_data_hora(data_hora),
                "tipo": tipo,
            }
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
        if input("Alterar tipo? [s/N]: ").strip().lower() == "s":
            dados["tipo"] = self._escolher_tipo()

        try:
            if data_hora:
                dados["data_hora"] = self._converter_data_hora(data_hora)
            self._facade.atualizar_lembrete(id_lembrete, dados)
            print("Lembrete atualizado com sucesso!")
        except (ValidacaoError, ValueError) as e:
            print(f"Erro: {e}")

    # Pede o id e aplica a ação sobre o lembrete correspondente.
    def _aplicar_por_id(self, titulo: str, acao, sucesso: str) -> None:
        print(f"\n--- {titulo} ---")
        id_lembrete = input("ID do lembrete: ")
        try:
            acao(id_lembrete)
            print(sucesso)
        except ValueError as e:
            print(f"Erro: {e}")

    def _concluir_lembrete(self) -> None:
        self._aplicar_por_id(
            "Concluir Lembrete",
            self._facade.concluir_lembrete,
            "Lembrete marcado como concluído!",
        )

    def _cancelar_lembrete(self) -> None:
        self._aplicar_por_id(
            "Cancelar Lembrete",
            self._facade.cancelar_lembrete,
            "Lembrete cancelado!",
        )

    def _remover_lembrete(self) -> None:
        self._aplicar_por_id(
            "Remover Lembrete",
            self._facade.remover_lembrete,
            "Lembrete removido com sucesso!",
        )

    def _listar_lembretes(self) -> None:
        print("\n--- Lista de Lembretes ---")
        self._exibir(self._facade.listar_lembretes(), "Nenhum lembrete cadastrado.")

    def _listar_lembretes_do_paciente(self) -> None:
        print("\n--- Lembretes do Paciente ---")
        email = input("Email do paciente: ")
        try:
            lembretes = self._facade.listar_lembretes_por_usuario(email)
        except ValueError as e:
            print(f"Erro: {e}")
            return
        self._exibir(lembretes, "O paciente não possui lembretes.")

    def _exibir(self, lembretes: list[LembreteSaude], vazio: str) -> None:
        if not lembretes:
            print(vazio)
            return
        for lembrete in lembretes:
            print(self._formatar(lembrete))

    # O id sai inteiro: é ele que as opções de atualizar e concluir pedem,
    # e a listagem é o único lugar onde o usuário pode consultá-lo.
    @staticmethod
    def _formatar(lembrete: LembreteSaude) -> str:
        return (
            f"[{lembrete.id_lembrete}] {lembrete.titulo} | "
            f"Tipo: {lembrete.tipo.value} | "
            f"Situação: {lembrete.situacao.value} | "
            f"Data: {lembrete.data_hora.strftime('%d/%m/%Y %H:%M')}"
        )

    def exibir_menu(self) -> None:
        """Exibe o menu de lembretes e processa a escolha do usuário."""
        while True:
            print("\n===== MedSense - Lembretes de Saúde =====")
            print("  [1] Criar lembrete")
            print("  [2] Atualizar lembrete")
            print("  [3] Concluir lembrete")
            print("  [4] Cancelar lembrete")
            print("  [5] Remover lembrete")
            print("  [6] Listar todos os lembretes")
            print("  [7] Listar lembretes de um paciente")
            print("  [0] Voltar ao menu principal")

            escolha = input("\nEscolha uma opção: ").strip()

            if escolha == "1":
                self._criar_lembrete()
            elif escolha == "2":
                self._atualizar_lembrete()
            elif escolha == "3":
                self._concluir_lembrete()
            elif escolha == "4":
                self._cancelar_lembrete()
            elif escolha == "5":
                self._remover_lembrete()
            elif escolha == "6":
                self._listar_lembretes()
            elif escolha == "7":
                self._listar_lembretes_do_paciente()
            elif escolha == "0":
                break
            else:
                print("Opção inválida. Tente novamente.")