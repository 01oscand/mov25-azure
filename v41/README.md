# V41 – Examination – Nordvik Fastigheter AB

## Översikt

Detta projekt är slutuppgiften i kursen Microsoft Azure.

Nordvik Fastigheter AB behöver en säker och skalbar hyresgästportal där en
hyresgäst kan logga in och registrera en felanmälan med:

- rubrik
- fastighet
- kategori
- beskrivning
- bild

Förvaltare ska kunna hantera felanmälningarna och ekonomi ska ha läsande
insyn.

Lösningen kombinerar Azure och Microsoft 365 och innehåller Compute, IAM,
nätverk, Storage, Infrastructure as Code och Power Automate.

---

## Arkitektur

```text
Hyresgäst
    │
    │ Microsoft Entra ID
    ▼
Azure Container Apps
ca-nordvik-portal
    │
    │ Managed Identity
    ▼
Azure Blob Storage
    │
    └── felanmalningar
          ├── reports/
          └── images/

Azure Container App
    │
    │ HTTP
    ▼
Power Automate
    │
    ├── SharePoint
    │     └── Felanmälningar
    │
    └── Outlook
          ├── normal notifiering
          └── akut notifiering
```

---

## Vald virtualiseringsnivå

Nordviks portal körs som en container i Azure Container Apps.

Container-nivån valdes eftersom Nordvik har varierande belastning och vill
undvika att betala för onödigt reserverad kapacitet.

En container ger mindre driftansvar än en virtuell maskin men behåller större
portabilitet och kontroll än en helt serverless lösning.

### Jämförelse

| Område | VM | Container | Serverless |
|---|---|---|---|
| Kontroll | Hög | Medel | Låg |
| Driftansvar | Högt | Medel | Lågt |
| Starttid | Minuter | Sekunder | Mycket snabb |
| Skalning | Mer manuell | Automatisk/snabb | Automatisk |
| Portabilitet | Lägre | Hög | Lägre |
| OS-underhåll | Ja | Nej | Nej |
| Nordvik | Möjligt | Vald nivå | Bra för mindre funktioner |

---

## Azure-resurser

Lösningen använder bland annat:

```text
Resource Group
rg-nordvik

Virtual Network
vnet-nordvik

Application subnet
snet-nordvik-app

Private Endpoint subnet
snet-nordvik-pe

Storage Account
stnordvikoscar01

Azure Container Registry
acrnordvikoscar01

Managed Identity
id-nordvik-portal

Container Apps Environment
cae-nordvik

Container App
ca-nordvik-portal

Log Analytics
law-nordvik

Private Endpoint
pe-nordvik-storage
```

---

## Applikation

Applikationsfilerna finns i:

```text
v41/app/
```

Strukturen är:

```text
app/
├── app.py
├── requirements.txt
└── Dockerfile
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
```

---

## Container image

Container-imagen byggs i Azure Container Registry.

```bash
az acr build \
  --registry acrnordvikoscar01 \
  --image nordvik-portal:v1 \
  .
```

Imagen lagras som:

```text
acrnordvikoscar01.azurecr.io/nordvik-portal:v1
```

---

## Authentication

Portalen använder Microsoft Entra ID.

Oautentiserade användare omdirigeras till Microsofts inloggning innan
applikationen kan användas.

Rollerna i lösningen är:

```text
SEC_Nordvik_Hyresgast
SEC_Nordvik_Forvaltare
SEC_Nordvik_Ekonomi
```

### Behörighetsmodell

```text
Hyresgäst
→ skapa felanmälan
→ se sina egna felanmälningar

Förvaltare
→ läsa och hantera ärenden

Ekonomi
→ läsbehörighet
```

---

## Managed Identity

Container App använder:

```text
id-nordvik-portal
```

som hanterad identitet.

Identiteten används för åtkomst till Azure-resurser utan att lösenord eller
Storage Keys behöver lagras i applikationskoden.

Roller inkluderar:

```text
Storage Blob Data Contributor
AcrPull
```

---

## Storage

Storage Account:

```text
stnordvikoscar01
```

används för felanmälningar och bilder.

Felanmälningar lagras ungefär enligt:

```text
felanmalningar/
├── reports/
│   └── <UUID>.json
│
└── images/
    └── <UUID>-image.jpg
```

Exempel på ärendedata:

```json
{
  "id": "UUID",
  "timestamp": "2026-10-06T12:00:00+00:00",
  "title": "Vatten under diskbänk",
  "description": "Det droppar vatten från röret.",
  "category": "Vatten",
  "property": "Nordvik 12",
  "tenant_email": "hyresgast.test@example.com",
  "image_blob": "images/UUID-bild.jpg",
  "status": "Ny"
}
```

---

## Storage-säkerhet

Storage konfigureras enligt defense in depth.

```text
Public Blob access:
Disabled

Public Network Access:
Disabled

HTTPS:
Required

Minimum TLS:
1.2
```

Storage nås via:

```text
Private Endpoint
+
Private DNS
+
Managed Identity
+
Azure RBAC
```

---

## Nätverk

Nordvik använder:

```text
vnet-nordvik
10.20.0.0/16
```

med separata subnät:

```text
snet-nordvik-app
10.20.0.0/23

snet-nordvik-pe
10.20.10.0/24
```

Private Endpoint används för Blob Storage.

---

## Defense in depth

Lösningen använder flera säkerhetslager:

```text
Microsoft Entra ID
        ↓
Container Apps Authentication
        ↓
HTTPS
        ↓
VNet
        ↓
Managed Identity
        ↓
Azure RBAC
        ↓
Private Endpoint
        ↓
Private Blob Storage
```

Det gör att säkerheten inte är beroende av en enda kontroll.

---

## Skalning

Container App är konfigurerad med:

```text
Minimum replicas: 2
Maximum replicas: 5
```

HTTP-baserad autoskalning används.

Två minsta repliker ger bättre tålighet mot att en enskild instans faller
bort.

Fler repliker kan startas vid hög belastning.

---

## Microsoft 365

Power Automate används för att integrera Azure med Microsoft 365.

Flödet:

```text
Nordvik Portal
      ↓
HTTP Request
      ↓
Power Automate
      ↓
SharePoint – Create item
      ↓
Outlook – Send email
      ↓
Condition
      ↓
Akut notifiering
```

---

## SharePoint

SharePoint-listan:

```text
Felanmälningar
```

fungerar som centralt ärenderegister.

Fälten inkluderar:

```text
Rubrik
Beskrivning
Kategori
Fastighet
Hyresgäst
Ärende-ID
Bildnamn
Status
Skapad tid
```

Statusvärden:

```text
Ny
Pågående
Avslutad
```

---

## Akuta felanmälningar

Följande kategorier behandlas som akuta:

```text
Värme
Vatten
Lås
```

Power Automate kontrollerar kategorin.

Vid akut kategori skickas en extra Outlook-notifiering med hög prioritet.

---

## Infrastructure as Code

Infrastructure as Code finns i:

```text
v41/iac/
```

Filer:

```text
iac/
├── azuredeploy.json
└── azuredeploy.parameters.json
```

ARM används bland annat för:

```text
Virtual Network
Subnets
Storage Account
Blob containers
Azure Container Registry
Managed Identity
Log Analytics
Tags
```

---

## Validera ARM-template

```bash
az deployment group validate \
  --resource-group rg-nordvik \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json
```

---

## What-if

```bash
az deployment group what-if \
  --resource-group rg-nordvik \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json
```

---

## Deployment

```bash
az deployment group create \
  --name nordvik-exam-infra \
  --resource-group rg-nordvik \
  --template-file azuredeploy.json \
  --parameters @azuredeploy.parameters.json
```

---

## Taggning

Resurser taggas för kostnadsuppföljning.

Exempel:

```text
Company = Nordvik
Environment = Exam
Department = IT
CostCenter = Portal
```

---

## Verifiering

Lösningen verifierades genom hela kedjan.

```text
1. Hyresgäst loggar in med Entra ID

2. Hyresgästen skickar felanmälan

3. Bild sparas i Blob Storage

4. JSON-data sparas i Blob Storage

5. Power Automate startar

6. SharePoint-post skapas

7. Outlook-notifiering skickas

8. Akut kategori skickar extra notifiering
```

Ytterligare verifiering gjordes av:

```text
Managed Identity
Azure RBAC
Private Endpoint
Storage nätverksbegränsning
Container App scaling
SharePoint-behörigheter
ARM deployment
```

---

## Kostnadsoptimering

Nordvik har ojämn trafik.

Container Apps valdes därför för att kunna anpassa kapaciteten efter
belastningen.

För Storage kan Lifecycle Management användas för att flytta äldre dokument
från Hot till Cool tier.

Exempel:

```text
0–90 dagar
→ Hot

Efter 90 dagar
→ Cool
```

---

## Säkerhetsprinciper

Följande säkerhetsprinciper används:

```text
Least privilege

Defense in depth

Managed Identity

Role-Based Access Control

Private networking

No public Blob access

No credentials in source code
```

---

## Hemligheter

Följande får inte versionshanteras:

```text
Storage Account Keys
ACR-lösenord
Power Automate HTTP URL
Client Secrets
Access tokens
```

Power Automate-URL lagras som secret i Container Apps och refereras via
environment variable.

---

## Avgränsning

Projektet är en examinationsmiljö.

Ett begränsat antal testkonton används för rollerna:

```text
Hyresgäst
Förvaltare
Ekonomi
```

I en produktionsmiljö med flera tusen externa hyresgäster skulle en mer
omfattande kundidentitets- och onboardinglösning behövas.

---

## Projektstruktur

```text
v41/
├── README.md
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── iac/
    ├── azuredeploy.json
    └── azuredeploy.parameters.json
```

---

## Slutsats

Lösningen kombinerar Azure Container Apps, Microsoft Entra ID, Managed
Identity, Azure Blob Storage, Private Endpoint, ARM och Power Automate.

Hyresgäster kan registrera felanmälningar genom en autentiserad portal.
Information och bilder lagras säkert i Azure och ärendena registreras
automatiskt i Microsoft 365.

Lösningen är byggd med fokus på:

- säkerhet
- skalbarhet
- least privilege
- defense in depth
- automatisering
- versionshantering
- kostnadsmedvetenhet