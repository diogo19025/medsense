# ADR-0001: Validação de campos no cadastro de usuário

- Status: Aceito
- Data: 2026-06-17

## Contexto

O Laboratório 2 exige tratamento de erros no cadastro de usuário, validando os
campos com exceções. As regras são:

- **Login**: obrigatório, no máximo 12 caracteres, sem números.
- **Senha**: política padrão do AWS IAM — 8 a 128 caracteres, ao menos 3 dos 4
  tipos de caractere (maiúsculas, minúsculas, números e símbolos) e diferente
  dos dados de identificação do usuário.

O diagrama de classes alvo define `Usuario` com `id`, `nome`, `email` e `senha`
— não há um campo de login. As regras de login (curto, sem números) não se
aplicam a `nome` nem a `email`.

## Decisão

1. Adicionar o campo `login` à entidade `Usuario`, pois as regras descrevem um
   identificador curto e sem números, incompatível com `nome` e `email`.
2. Centralizar as regras na classe dedicada `ValidadorUsuario`, mantendo as
   validações coesas e testáveis.
3. Disparar a validação em `Usuario.__post_init__`, garantindo que nenhum
   usuário inválido seja construído.
4. Representar as falhas com exceções de domínio (`LoginInvalidoError`,
   `SenhaInvalidaError`), tratadas na camada de fronteira (CLI).

## Consequências

- O campo `login` diverge do diagrama de classes atual; o diagrama deve ser
  atualizado no item 1 do laboratório (fora do escopo deste trabalho).
- A política de senha segue o padrão do AWS IAM referenciado no enunciado.
- A validação fica desacoplada da interface, podendo ser reutilizada por outros
  mecanismos de entrada no futuro.

## Referências

- AWS IAM — política de senhas padrão:
  https://docs.aws.amazon.com/pt_br/IAM/latest/UserGuide/id_credentials_passwords_account-policy.html
