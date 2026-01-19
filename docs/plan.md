# Plan projekta

## Naziv projekta
Dizajn i implementacija sustava za upravljanje privilegiranim pristupom (Privileged Access Management – PAM)

## Opis projekta
Privilegirani korisnički računi predstavljaju jedan od najvećih sigurnosnih rizika u suvremenim informacijskim sustavima. Takvi računi imaju široke ovlasti te omogućuju pristup osjetljivim resursima, konfiguracijama i podacima. Zbog toga njihova zlouporaba ili kompromitacija može dovesti do ozbiljnih sigurnosnih incidenata.

Cilj ovog projekta je dizajnirati i implementirati funkcionalni prototip sustava za upravljanje privilegiranim pristupom (PAM) namijenjen internim poslovnim okruženjima. Sustav omogućuje centralizirano upravljanje privilegiranim vjerodajnicama, kontrolu pristupa temeljem uloga, privremeni (Just-in-Time) pristup te nadzor i bilježenje privilegiranih sesija.

Projekt je implementiran kao prototip korištenjem otvorenih tehnologija te nije namijenjen produkcijskoj upotrebi, već demonstraciji ključnih koncepata i sigurnosnih mehanizama PAM sustava.

## Ciljevi projekta
Glavni ciljevi projekta su:
- Analizirati sigurnosne izazove povezane s privilegiranim pristupom.
- Dizajnirati arhitekturu PAM sustava u skladu s dobrim sigurnosnim praksama.
- Implementirati sustav koji omogućuje sigurnu pohranu privilegiranih vjerodajnica.
- Omogućiti vremenski ograničen pristup privilegiranim resursima.
- Implementirati nadzor i reviziju privilegiranih aktivnosti.
- Evaluirati funkcionalnost i sigurnost sustava.

## Opseg projekta

### U opsegu projekta
- Centralizirana pohrana privilegiranih vjerodajnica.
- Upravljanje pristupom temeljem uloga (RBAC).
- Just-in-Time (JIT) zahtjevi za privilegirani pristup.
- Proces odobravanja pristupa.
- Bilježenje i snimanje privilegiranih sesija.
- Administratorsko web sučelje za upravljanje pristupima.

### Izvan opsega projekta
- Produkcijska implementacija i visoka dostupnost.
- Integracija s vanjskim cloud servisima.
- Komercijalna PAM rješenja i licenciranje.

## Metodologija i vremenski plan
Projekt je podijeljen u nekoliko faza koje omogućuju postupni razvoj i evaluaciju sustava.

| Faza | Opis | Trajanje |
|-----|------|----------|
| Faza 1 | Analiza problema i istraživanje literature | 1.–3. tjedan |
| Faza 2 | Dizajn arhitekture sustava | 4.–6. tjedan |
| Faza 3 | Implementacija PAM prototipa | 7.–12. tjedan |
| Faza 4 | Testiranje i evaluacija | 13.–15. tjedan |
| Faza 5 | Izrada dokumentacije i prezentacija | 16.–17. tjedan |

## Korišteni alati i tehnologije
- Python (FastAPI) za backend logiku
- React (Vite) za frontend sučelje
- PostgreSQL za pohranu podataka
- HashiCorp Vault za sigurno upravljanje vjerodajnicama
- Docker i Docker Compose za kontejnerizaciju sustava
- JWT i MFA (TOTP) za autentikaciju i autorizaciju
