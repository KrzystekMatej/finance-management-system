## First time setup (windows)
```bash
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

```

## If project is already setup
```bash
.\env\Scripts\activate
python manage.py migrate
python manage.py runserver
```

## If you want to check it on the phone
```bash
python manage.py runserver 0.0.0.0:8000
```
1. Find your PC's local IP with ipconfig
2. Add it to ALLOWED_HOSTS in finance-management-system/project/settings.py
3. Connect to that IP with same port on your phone

## Resources

[Google doc](https://docs.google.com/document/d/1CBFf9SYnnrxeE0lQ2UtjCQK5ZHMXkhcF/edit?usp=sharing&ouid=106305257367534443251&rtpof=true&sd=true)

[UI mockup](https://www.figma.com/design/eYu9ELOc3WdKGwBth3F1sO/Untitled?node-id=0-1&node-type=canvas)

## UML diagram test

```mermaid
classDiagram
    class Zakaznik {
        +String jmeno
        +String prijmeni
        +int id
        +String adresa
        +String telefon
        +void zalozitUcet(BankovniUcet ucet)
        +void pridatSpolecnyUcet(SpolecnyUcet ucet)
    }

    class BankovniUcet {
        +String cisloUctu
        +double zbytek
        +Date datumZalozeni
        +List~Transaction~ historieTransakci
        +void ulozitTransakci(Transaction transakce)
    }

    class SpolecnyUcet {
        +String cisloUctu
        +double zbytek
        +void pridatVlastnika(Zakaznik zakaznik)
        +List~Zakaznik~ vlastnici
    }

    class Transaction {
        +double castka
        +String datum
        +String typ
        +String popis
    }

    class KreditniKarta {
        +String cisloKarty
        +double limit
        +double aktualniDluh
        +String datumPlatnosti
        +void provestPlatbu(double castka)
    }

    class Pojisteni {
        +String typPojisteni
        +double castka
        +Date datumSplatnosti
        +void vypocitatSplatku()
    }

    class Adresa {
        +String ulice
        +String mesto
        +String psc
    }

    class Zamestnanec {
        +String jmeno
        +String prijmeni
        +int id
        +String pozice
        +double plat
    }

    Zakaznik "1" --> "N" BankovniUcet : vlastni
    Zakaznik "0..*" --> "N" KreditniKarta : vlastniKartu
    Zakaznik "1" --> "0..*" Adresa : bydliNa
    BankovniUcet "1" --> "0..*" Transaction : ma
    BankovniUcet "0..1" --> "0..*" SpolecnyUcet : spolecny
    KreditniKarta "1" --> "0..*" Transaction : transakce
    Zakaznik "1" --> "0..*" Pojisteni : maPojisteni
    Pojisteni "1" --> "1" BankovniUcet : pojisteniUhrada
    Zamestnanec "1" --> "1..*" BankovniUcet : spravuje

```
