# Dizajn i implementacija PAM sustava

## 1. Uvod

Privilegirani računi (npr. administrator, root, servisni računi, računi za održavanje i automatizaciju) predstavljaju najkritičniju kategoriju identiteta u informacijskom sustavu jer posjeduju široke ovlasti: pristup konfiguraciji, korisničkim podacima, sigurnosnim postavkama i resursima visoke vrijednosti. U praksi, kompromitacija privilegiranog računa često znači kompromitaciju cijelog sustava ili domene.

Upravo zato Privileged Access Management (PAM) pristup ne promatra privilegirani pristup kao “još jednu prijavu”, nego kao kontrolirani proces s jasnim pravilima: tko smije zatražiti pristup, pod kojim uvjetima, koliko dugo, preko kojeg kanala i uz koje obavezne nadzorne mehanizme.

Cilj projekta je izrada prototipa PAM sustava koji demonstrira temeljne sigurnosne principe:

- minimizacija trajnih privilegija (princip najmanjih ovlasti),
- privremeni pristup (Just-in-Time),
- odobravanje (approval) i evidencija (audit),
- centralizirani nadzor privilegiranih sesija preko gateway-a,
- odvajanje aplikacije od stvarnih vjerodajnica (vault koncept).

Projekt je zamišljen kao “proof-of-concept” koji daje jasnu sliku kako bi se PAM mogao dizajnirati u realnom okruženju, uz naglasak na sigurnosnu logiku i proces pristupa.


## 2. Ciljevi i zahtjevi sustava

### 2.1 Funkcionalni ciljevi

Sustav mora omogućiti:

1. Korisničku prijavu i izdavanje tokena za rad s API-jem  
2. Uloge i politike pristupa (RBAC) za razlikovanje ovlasti  
3. Zahtjev za privilegiranim pristupom (JIT request)  
4. Odobravanje zahtjeva od strane administratora (ili ovlaštenog odobravatelja)  
5. Vremenski ograničen pristup (npr. 15/30/60 minuta)  
6. Posredovanje sesije kroz gateway (nadzor i evidencija)  
7. Reviziju (audit): trag tko je što radio i kada  

### 2.2 Sigurnosni ciljevi

Sustav mora smanjiti tipične rizike privilegiranog pristupa:

- izbjegavanje trajnih admin prava “za svaki slučaj”  
- sprječavanje dijeljenja lozinki među članovima tima  
- smanjenje izlaganja privilegiranih vjerodajnica (vault i reference)  
- mogućnost forenzičke analize (audit i session evidence)  
- zaštita administrativnih radnji dodatnim slojem autentikacije (MFA)  


## 3. Arhitektura sustava

Sustav je implementiran kao kontejnerizirana aplikacija sastavljena od više komponenti. Takav dizajn omogućuje:

- modularno razvijanje i testiranje  
- jasnu podjelu odgovornosti  
- izolaciju rizika (npr. trezor i gateway su odvojene cjeline)  
- lakše skaliranje i zamjenu pojedinih komponenti  

### 3.1 Komponente (logički prikaz)

#### (1) PAM aplikacija / API
- centralna logika sustava  
- autentikacija (JWT), autorizacija (RBAC)  
- upravljanje korisnicima, ulogama, resursima  
- upravljanje zahtjevima i odobrenjima (JIT)  

#### (2) Trezor (Vault)
- sigurno čuvanje privilegiranih vjerodajnica (ili tajni)  
- PAM aplikacija ne “sprema lozinke” u vlastite tablice, nego koristi reference (ID / path)  
- kontrola tko i kada smije dohvatiti tajnu (ako je potrebno)  

#### (3) Gateway / Session Proxy
- obavezna “točka prolaza” za privilegirane sesije  
- omogućuje centralizirani nadzor  
- služi kao mjesto gdje se bilježe aktivnosti i gdje se može snimati sesija (ovisno o prototipu)  

#### (4) Baza podataka
- pohrana korisnika, uloga, politika, zahtjeva, logova  
- čuva “state” sustava (npr. je li zahtjev odobren, do kada vrijedi, tko je odobrio)  

#### (5) Audit / Logging sloj
- centralizirano bilježenje događaja (logovi)  
- zapis minimalno uključuje: tko, što, kada, odakle, rezultat (uspjeh/neuspjeh)  


## 4. Model prijetnji i sigurnosna logika

PAM sustav adresira realne scenarije prijetnji:

- krađa lozinki (phishing, malware, reuse lozinki)  
- zlouporaba legitimnog admina (insider threat)  
- eskalacija privilegija kroz slabe kontrole  
- nepostojanje revizije (nemoguće dokazati tko je što radio)  
- curenje vjerodajnica kroz konfiguracije, logove ili repositorije  

Zato dizajn naglašava:

- pristup privilegijama samo kada treba (JIT)  
- odobravanje i vremensko ograničenje  
- minimalno izlaganje tajni  
- audit i (idealno) session evidence  


## 5. Implementacija sustava

### 5.1 Autentikacija (JWT) i upravljanje sesijom korisnika

Korisnik se autentificira prijavom (username/password ili sličan mehanizam). Nakon uspješne prijave sustav izdaje JWT token koji se koristi kao dokaz identiteta pri svakom pozivu API-ja.

Token tipično sadrži:
- identitet korisnika (user_id)  
- ulogu/ovlasti (role/claims)  
- vrijeme isteka (exp)  
- potpis (signature) koji osigurava integritet  

Prednost JWT-a je stateless provjera identiteta, no u PAM kontekstu važno je voditi računa o:
- kratkom životnom vijeku tokena  
- mogućnosti revokacije (blacklist/rotate)  
- sigurnom spremanju tokena na klijentu  

### 5.2 Autorizacija (RBAC) i politike

Autorizacija je bazirana na ulogama (RBAC).

- Korisnik može zatražiti pristup i vidjeti svoje zahtjeve  
- Administrator/Approver može odobravati ili odbijati zahtjeve i upravljati resursima  
- Administratorske akcije dodatno su zaštićene MFA-om  

U naprednijoj varijanti RBAC se može proširiti u ABAC model, uz atribute poput:
- vrijeme dana  
- IP adresa / lokacija  
- tip resursa  
- rizik zahtjeva  
- status korisnika  

### 5.3 Višefaktorska autentikacija (MFA)

MFA je dodatni sigurnosni sloj za kritične operacije.

U prototipu je implementiran kroz:
- jednokratne kodove (TOTP)  
- step-up autentikaciju  
- vremenski ograničene potvrde  

## 6. Upravljanje vjerodajnicama (Vault pristup)

Aplikacija ne posjeduje trajno privilegirane lozinke.

- vjerodajnice su pohranjene u trezoru  
- PAM aplikacija koristi reference (credential_id)  
- pristup tajni je strogo kontroliran  

Ovim se postiže manji rizik curenja, lakša rotacija i centralna kontrola pristupa.


## 7. Just-in-Time (JIT) pristup i workflow odobravanja

### 7.1 Logika zahtjeva

Korisnik podnosi zahtjev s definiranim parametrima:
- traženi resurs  
- potrebne ovlasti  
- trajanje pristupa  
- razlog zahtjeva  

Zahtjev prelazi u stanje **PENDING**.

### 7.2 Odobravanje i aktivacija

Administrator:
- odobrava (**APPROVED**) ili odbija (**REJECTED**)  
- generira vremenski prozor (valid_from / valid_to)  
- kreira JIT grant koji provjerava gateway  

### 7.3 Automatsko ukidanje

Po isteku vremena pristup se automatski ukida (**EXPIRED**).


## 8. Upravljanje sesijama (Gateway i nadzor)

Privilegirane sesije prolaze kroz gateway koji provjerava:
- postojanje važećeg JIT granta  
- vremensko ograničenje  
- razinu ovlasti  

Bilježe se:
- user_id i resource_id  
- start_time i end_time  
- rezultat sesije  
- opcionalno izvršene akcije  


## 9. Revizija i audit (praćenje tragova)

Sustav bilježi:
- pokušaje prijave  
- JIT zahtjeve i odluke  
- početak i kraj sesija  
- neovlaštene pokušaje  
- administrativne promjene  

Audit omogućuje forenziku, usklađenost i detekciju anomalija.


## 10. Testiranje i evaluacija

### 10.1 Funkcionalni scenariji
1. Login → JWT → zahtjev  
2. RBAC provjera  
3. Odobravanje zahtjeva  
4. Pristup unutar vremena  
5. Odbijanje nakon isteka  

### 10.2 Sigurnosni scenariji
1. Pristup bez JIT-a → blokada  
2. Admin bez MFA → blokada  
3. Istečeni grant → odbijanje  
4. Audit zapis za svaki događaj  

### 10.3 Evaluacija

Postignuta je redukcija trajnih privilegija, jasna odgovornost i revizija.


## 11. Ograničenja prototipa

Sustav ne uključuje:
- UEBA analitiku  
- AD/LDAP/SSO integracije  
- potpunu rotaciju tajni  
- napredni session recording  
- SOAR automatizaciju  


## 12. Preporuke za poboljšanja

1. Automatska rotacija lozinki  
2. ABAC i risk-based odluke  
3. Session recording  
4. Integracija s SSO-om  
5. SOAR-like reakcije  
6. Napredna revizija  


## 13. Zaključak

PAM prototip pokazuje kako se privilegirani pristup može kontrolirati kroz privremene ovlasti, odobravanje, nadzor i reviziju. Sustav smanjuje rizik zlouporabe privilegiranih računa i povećava vidljivost nad kritičnim radnjama, predstavljajući čvrstu osnovu za daljnji razvoj prema produkcijskim PAM rješenjima.
