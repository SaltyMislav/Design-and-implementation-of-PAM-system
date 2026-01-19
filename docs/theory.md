# Teorijska pozadina

## Uvod u upravljanje privilegiranim pristupom
U suvremenim informacijskim sustavima sigurnost više ne ovisi isključivo o zaštiti mrežne infrastrukture ili aplikacija, već sve više o kontroli pristupa korisnika s povišenim ovlastima. Privilegirani korisnički računi imaju mogućnost upravljanja sustavima, pristupa osjetljivim podacima te izvođenja radnji koje mogu značajno utjecati na sigurnost i stabilnost cijelog informacijskog sustava.

Zbog navedenog, upravljanje privilegiranim pristupom (Privileged Access Management – PAM) postaje ključna komponenta cjelokupne sigurnosne arhitekture organizacija.

## Privileged Access Management (PAM)
Privileged Access Management predstavlja skup politika, procesa i tehničkih rješenja koja omogućuju kontrolu, nadzor i reviziju pristupa privilegiranim računima. Cilj PAM sustava nije samo sprječavanje neovlaštenog pristupa, već i smanjenje rizika povezanog s legitimnim korištenjem privilegija.

PAM sustavi omogućuju organizacijama da:
- ograniče trajanje privilegiranog pristupa
- nadziru aktivnosti korisnika
- osiguraju odgovornost i sljedivost radnji
- smanje posljedice eventualne kompromitacije

## Privilegirani računi i sigurnosni izazovi
Privilegirani računi uključuju administratorske račune operacijskih sustava, račune baza podataka, servisne račune te druge račune s povećanim ovlastima. U praksi se često susreću sljedeći sigurnosni problemi:
- korištenje istih administratorskih vjerodajnica dulje vremensko razdoblje
- dijeljenje privilegiranih računa između više korisnika
- nedostatak evidencije tko je i kada koristio privilegirani pristup
- ograničena mogućnost otkrivanja zlouporaba

Napadači često ciljaju upravo takve račune jer im omogućuju potpunu kontrolu nad sustavom nakon uspješne kompromitacije.

## Centralizirana pohrana vjerodajnica
Jedan od temeljnih elemenata PAM sustava je centralizirani trezor vjerodajnica. Trezor omogućuje sigurno pohranjivanje osjetljivih podataka kao što su lozinke, privatni ključevi i tokeni korištenjem kriptografskih mehanizama.

Korisnici ne dobivaju izravan pristup vjerodajnicama, već sustav koristi vjerodajnice u njihovo ime prilikom uspostave sesije. Time se značajno smanjuje rizik od curenja osjetljivih podataka.

## Upravljanje pristupom temeljem uloga (RBAC)
Role-Based Access Control (RBAC) predstavlja model kontrole pristupa u kojem se ovlasti dodjeljuju prema ulogama, a ne pojedinačnim korisnicima. Na taj način se pojednostavljuje upravljanje pravima i smanjuje rizik dodjele prevelikih ovlasti.

U kontekstu PAM sustava, RBAC omogućuje:
- precizno definiranje privilegija
- lakše upravljanje korisnicima
- bolju usklađenost sa sigurnosnim politikama

## Just-in-Time (JIT) pristup
Just-in-Time pristup omogućuje dodjelu privilegiranih ovlasti samo kada su potrebne i samo na ograničeno vremensko razdoblje. Nakon isteka tog razdoblja, pristup se automatski ukida.

Prednosti JIT pristupa uključuju:
- smanjenje napadne površine
- ograničavanje trajanja potencijalne zlouporabe
- bolju kontrolu i pregled nad privilegiranim aktivnostima

JIT pristup predstavlja važan mehanizam u modernim PAM rješenjima.

## Višefaktorska autentikacija (MFA)
Višefaktorska autentikacija (Multi-Factor Authentication – MFA) predstavlja dodatni sloj sigurnosti koji zahtijeva korištenje više nezavisnih faktora autentikacije. U kontekstu PAM sustava, MFA se često koristi za zaštitu administratorskih funkcija i osjetljivih radnji.

Korištenjem MFA smanjuje se rizik kompromitacije privilegiranih računa čak i u slučaju krađe lozinki.

## Nadzor i snimanje privilegiranih sesija
Nadzor i snimanje sesija omogućuju detaljan uvid u aktivnosti korisnika tijekom korištenja privilegiranog pristupa. Takav pristup omogućuje:
- reviziju i forenzičku analizu
- dokazivanje odgovornosti korisnika
- otkrivanje sumnjivih aktivnosti

Snimanje sesija predstavlja važan alat u sprječavanju i istraživanju sigurnosnih incidenata.

## Sigurnosni standardi i preporuke
Projekt se temelji na preporukama i smjernicama sljedećih standarda i organizacija:
- NIST SP 800-53 – Access Control
- ISO/IEC 27001 – Upravljanje informacijskom sigurnošću
- OWASP Secure Coding Practices

Ovi standardi pružaju smjernice za implementaciju sigurnih sustava i upravljanje privilegiranim pristupom.

## Sažetak teorijske osnove
Upravljanje privilegiranim pristupom predstavlja ključni sigurnosni izazov modernih informacijskih sustava. PAM sustavi omogućuju organizacijama da smanje rizike povezane s privilegiranim računima kroz kontrolu, nadzor i reviziju pristupa. Teorijska osnova predstavljena u ovom poglavlju služi kao temelj za dizajn i implementaciju PAM prototipa opisanog u nastavku rada.
