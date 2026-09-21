# V38 – Infrastructure as Code

Under vecka 38 används ARM-templates för att provisionera
centrala delar av Novatrix Azure-miljö.

## Provisionerade resurser

- Virtual Network: `vnet-novatrix-iac`
- Subnet: `snet-web`
- Network Security Group: `nsg-web-iac`
- Webregel för TCP 80 och 443
- Azure Storage Account

## Filer

- `azuredeploy.json` – ARM-template
- `azuredeploy.parameters.json` – parametervärden

## Validering

```bash
az deployment group validate \
  --resource-group rg-novatrix \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json

## What-If

az deployment group what-if \
  --resource-group rg-novatrix \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json

## Deployment
az deployment group create \
  --name novatrix-v38-deployment \
  --resource-group rg-novatrix \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json

## Verifiering
az resource list \
  --resource-group rg-novatrix \
  -o table