"""Auxiliares de entrada de dados compartilhados pelas views."""


# Converte "a, b, c" numa lista de itens sem espaços sobrando.
def ler_lista(rotulo: str) -> list[str]:
    entrada = input(f"{rotulo} (separadas por vírgula, vazio para nenhuma): ")
    return [item.strip() for item in entrada.split(",") if item.strip()]
