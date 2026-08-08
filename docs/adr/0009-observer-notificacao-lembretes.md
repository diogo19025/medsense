# ADR-0009: Observer para notificações de lembretes

- Status: Aceito
- Data: 2026-08-06

## Contexto

O sistema agora possui a funcionalidade de "Lembretes de Saúde". É necessário que, sempre que um lembrete for criado, atualizado ou concluído, ações secundárias sejam disparadas (como registro em log, envio de e-mails, alertas no console ou notificações na interface gráfica). 

Se colocássemos toda a lógica de notificação diretamente dentro da classe `LembreteControl`, violaríamos o Princípio de Responsabilidade Única (SRP) e criaríamos um alto acoplamento entre a regra de negócio do lembrete e os mecanismos de envio de notificação.

## Decisão

Optamos por implementar o padrão de projeto **Observer** (Comportamental). 

- A controladora `LembreteControl` atuará como o **Subject** (Sujeito), mantendo uma lista de observadores e notificando-os sobre mudanças de estado (criado, atualizado, concluído, cancelado e removido).
- Criamos a interface `ObservadorLembrete` para garantir que todos os ouvintes sigam o mesmo contrato.
- Criamos implementações concretas como `NotificadorConsole` e `RegistroNotificacaoObserver` (que faz uso da nossa porta `Logger`).
- A notificação acontece depois de a mutação já estar aplicada na coleção, e cada observador é acionado isoladamente: uma falha é registrada pela porta `Logger` e não interrompe os demais nem devolve erro a quem pediu a operação. Sem esse isolamento, um observador com defeito faria a boundary exibir erro sobre um lembrete que, na prática, já existia.

## Consequências

**Positivas:**
- **Baixo Acoplamento:** A controladora de lembretes não sabe como as notificações são enviadas, apenas que existem interessados no evento.
- **Extensibilidade:** Se no futuro precisarmos enviar notificações por WhatsApp ou e-mail, basta criar uma nova classe que implemente `ObservadorLembrete` e anexá-la, sem modificar a controladora.

**Negativas:**
- Adiciona uma ligeira complexidade à camada de controle.
- A ordem de execução dos observadores não é garantida, o que exige que as implementações sejam independentes entre si.
- Como as falhas de notificação são engolidas e apenas registradas, um observador quebrado passa despercebido por quem usa o sistema — o log é o único lugar onde o problema aparece.

## Referências

- ADR-0003: Adapter para biblioteca de log (porta `Logger` usada pelo `RegistroNotificacaoObserver`).
- ADR-0006: CRUD de Perfil de Saúde (desenho de controle e coleção seguido pelo `LembreteControl`).
