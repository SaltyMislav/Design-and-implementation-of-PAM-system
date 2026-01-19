# Dizajn i implementacija PAM sustava

## Uvod
Upravljanje privilegiranim pristupom predstavlja ključni element informacijske sigurnosti. Cilj ovog projekta je izrada prototipa PAM sustava koji omogućuje kontroliran, vremenski ograničen i nadziran pristup privilegiranim resursima.

## Arhitektura sustava
Sustav je implementiran kao kontejnerizirana aplikacija sastavljena od više komponenti koje međusobno komuniciraju. Takav pristup omogućuje modularnost, lakše testiranje i izolaciju pojedinih dijelova sustava.

## Implementacija sustava

### Autentikacija i autorizacija
Autentikacija korisnika provodi se pomoću JWT tokena, dok je autorizacija temeljena na ulogama. Administratorske radnje dodatno su zaštićene višefaktorskom autentikacijom.

### Upravljanje vjerodajnicama
Privilegirane vjerodajnice pohranjuju se u trezor, dok aplikacija koristi samo reference na njih, čime se smanjuje rizik od curenja osjetljivih podataka.

### Just-in-Time pristup
Sustav omogućuje korisnicima podnošenje zahtjeva za privremeni pristup, koji mora biti odobren od strane administratora.

### Upravljanje sesijama
Privilegirane sesije prolaze kroz gateway komponentu koja omogućuje nadzor i snimanje aktivnosti.

## Testiranje i evaluacija
Sustav je testiran kroz funkcionalne i sigurnosne scenarije, uključujući simulaciju zlouporabe privilegiranog pristupa.

## Ograničenja sustava
Sustav je prototip i ne uključuje sve značajke komercijalnih PAM rješenja.

## Zaključak
Projekt demonstrira osnovne principe PAM sustava i naglašava važnost kontroliranog pristupa privilegiranim računima.
