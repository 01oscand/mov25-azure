# V40 – Virtualiseringsnivåer

Under vecka 40 jämförs tre virtualiseringsnivåer:

- Virtuell maskin
- Container
- Serverless

Novatrix kundtjänst har tidigare körts på en virtuell maskin.
Som alternativ nivå körs en del av webbapplikationen som en
container i Azure Container Instances.

## Lösning

Dockerfile
→ Container image
→ Azure Container Registry
→ Azure Container Instances
→ Publik webbadress

## Azure-resurser

Resource Group:
rg-novatrix

Container Registry:
novatrixacroscar40

Container Instance:
novatrix-app-v40