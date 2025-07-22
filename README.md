# Pass Secret App v1.0

Een minimalistische webapplicatie om tijdelijke geheime berichten veilig te delen via unieke links. De link is slechts een beperkt aantal keer te bekijken en vervalt daarna automatisch.

---

## Functionaliteit

- Maak tijdelijke, geheime berichten aan
- Genereert unieke, moeilijk te raden UUID-links
- AES-encryptie (symmetric key) – sleutel wordt geladen vanuit `.env`
- Beperk het aantal keer dat een geheim bekeken mag worden
- Verwijdert automatisch geheimen na het maximale aantal views
- Cleanup-route beschikbaar voor handmatig opruimen
- Custom 404-pagina bij verlopen of foutieve links
- Cloudflare Tunnel (optioneel) voor publieke toegang
- Voeg via `.env` eigen kleuren toe
- Voeg aan de map `static` je eigen logo toe

---

## Technische stack

- Backend: Python 3 + Flask
- Database: SQLite (tijdelijke opslag)
- Encryptie: AES via de `cryptography`-bibliotheek
- Frontend: Minimalistische HTML en CSS
- Deployment: Docker + docker-compose

---

## Installatie via Docker

### Vereisten

- Docker
- Docker Compose
- Een `.env` bestand met encryptiesleutel (zie hieronder)

### `.env` bestand

Maak een `.env` bestand aan in de root van het project met minimaal de volgende variabele:

```env
SECRET_KEY=je_super_geheime_sleutel
BACKGROUND_COLOR=#f0f0f0
BUTTON_COLOR=#0066cc
