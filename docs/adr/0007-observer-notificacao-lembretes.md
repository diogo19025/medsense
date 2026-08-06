# 7. Uso do Padrão Observer para Notificações de Lembretes

Data: 2026-08-06

## Status

Aceito

## Contexto

O sistema agora possui a funcionalidade de "Lembretes de Saúde". É necessário que, sempre que um lembrete for criado, atualizado ou concluído, ações secundárias sejam disparadas (como registro em log, envio de e-mails, alertas no console ou notificações na interface gráfica). 

Se colocássemos toda a lógica de notificação diretamente dentro da classe `LembreteControl`, violaríamos o Princípio de Responsabilidade Única (SRP) e criaríamos um alto acoplamento entre a regra de negócio do lembrete e os mecanismos de envio de notificação.

## Decisão

Optamos por implementar o padrão de projeto **Observer** (Comportamental). 

- A controladora `LembreteControl` atuará como o **Subject** (Sujeito), mantendo uma lista de observadores e notificando-os sobre mudanças de estado (criado, atualizado, concluído).
- Criamos a interface `ObservadorLembrete` para garantir que todos os ouvintes sigam o mesmo contrato.
- Criamos implementações concretas como `NotificadorConsole` e `RegistroNotificacaoObserver` (que faz uso da nossa porta `Logger`).

## Consequências

**Positivas:**
- **Baixo Acoplamento:** A controladora de lembretes não sabe como as notificações são enviadas, apenas que existem interessados no evento.
- **Extensibilidade:** Se no futuro precisarmos enviar notificações por WhatsApp ou e-mail, basta criar uma nova classe que implemente `ObservadorLembrete` e anexá-la, sem modificar a controladora.

**Negativas:**
- Adiciona uma ligeira complexidade à camada de controle.
- A ordem de execução dos observadores não é garantida, o que exige que as implementações sejam independentes entre si.