# Azure – Vecka 39
## Automation och integration

Under vecka 39 integreras Novatrix Azure-baserade
kundtjänstlösning med Microsoft 365 genom Power Automate.

När ett nytt kundärende skapas ska informationen registreras
automatiskt i SharePoint och kundtjänsten ska få en
e-postnotis via Outlook.

## Händelsekedja

Kundtjänstformulär
→ Azure Storage
→ Power Automate
→ SharePoint
→ Outlook

# V39 – Automation och integration

## Syfte

Syftet med uppgiften är att integrera Novatrix
Azure-baserade kundtjänstlösning med Microsoft 365.

## Lösning

När ett kundärende skickas genom webbformuläret lagras
informationen i Azure Storage.

Power Automate reagerar på det nya ärendet, läser JSON-data
och skapar automatiskt ett listobjekt i SharePoint.

Efter registreringen skickas en e-postnotis till
kundtjänsten via Outlook.

## Händelsekedja

Webbformulär
→ Azure Storage
→ Power Automate
→ Parse JSON
→ SharePoint
→ Outlook

## Microsoft 365

SharePoint-lista:
Novatrix Ärenden

Notifiering:
Office 365 Outlook

## Verifiering

Lösningen verifierades genom ett end-to-end-test.

1. Ett ärende skickades genom Novatrix webbformulär.
2. Ärendet lagrades i Azure Storage.
3. Power Automate-flödet startades automatiskt.
4. Ett nytt ärende skapades i SharePoint.
5. En e-postnotis skickades via Outlook.

Power Automate Run History visade att samtliga steg
genomfördes utan fel.