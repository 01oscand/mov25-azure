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

# V40 – Virtualiseringsnivåer

## Syfte

Novatrix kundtjänst har tidigare körts på en virtuell maskin.
Under V40 körs en del av webbapplikationen som en container
för att jämföra olika virtualiseringsnivåer.

## Containerlösning

Dockerfile
→ Azure Container Registry
→ Azure Container Instances
→ Publik webbadress

## Filer

- `container/Dockerfile`
- `container/index.html`

## Bygg image

```bash
az acr build \
  --registry novatrixacroscar40 \
  --image novatrix-app:v1 \
  .
  