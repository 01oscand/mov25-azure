# V38 – Infrastructure as Code

Under vecka 38 används Infrastructure as Code med ARM-templates
för att provisionera centrala delar av Novatrix Azure-miljö.

## Resurser

ARM-templaten provisionerar:

- Virtual Network
- Subnet
- Network Security Group
- Webregel för TCP 80 och 443
- Azure Storage Account

Miljön är parametriserad för att templaten ska kunna återanvändas.

## Deployment

Deployment sker med Azure CLI mot resursgruppen `rg-novatrix`.

Före deployment används `validate` och `what-if` för att kontrollera
templaten och vilka förändringar Azure planerar att genomföra.