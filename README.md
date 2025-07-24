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
- **Statistiekenpagina met overzicht van alle geheimen en views**
- **Grafische weergave van geheimen per dag via Chart.js**
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
- **Statistieken: Chart.js voor grafieken**
- Deployment: Docker + docker-compose

---

## Routes

- `/` - Hoofdpagina voor het aanmaken van geheimen
- `/<uuid>` - Bekijken van geheime berichten
- `/admin/stats` - Statistiekenoverzicht met grafieken
- `/cleanup` - Handmatige cleanup van verlopen geheimen

---

## Installatie via Docker

### Vereisten

- Docker
- Docker Compose
- Een `.env` bestand met encryptiesleutel (zie hieronder)

### `.env` bestand

Genereer een Secret key door middel van ```python -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"```
Maak een `.env` bestand aan in de root van het project met minimaal de volgende variabele:

```env
SECRET_KEY=je_super_geheime_sleutel
BACKGROUND_COLOR=#f0f0f0
BUTTON_COLOR=#0066cc
ADMIN_USERNAME=<username>
ADMIN_PASSWORD=<pass>
```
