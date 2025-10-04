# Krakowskie Cyfrowe Centrum Wolontariatu - Backend API

## 📋 Opis projektu

Backend aplikacji łączącej młodych wolontariuszy z organizacjami i instytucjami działającymi na terenie Krakowa. System umożliwia:

- **Wolontariuszom**: przeglądanie i zgłaszanie się do inicjatyw
- **Organizacjom**: tworzenie inicjatyw, zarządzanie zgłoszeniami, wystawianie zaświadczeń
- **Koordynatorom szkolnym**: monitorowanie uczniów i generowanie raportów

## 🚀 Szybki start

### 1. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 2. Inicjalizacja bazy danych

```bash
python init_database.py
```

To utworzy bazę SQLite z przykładowymi danymi:
- 10 wolontariuszy
- 7 organizacji
- 3 koordynatorów szkolnych
- 15 inicjatyw wolontariackich
- ~30 uczestnictw
- ~10 zaświadczeń

### 3. Uruchomienie serwera

```bash
python main.py
```

lub:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Dostęp do API

- **API**: http://localhost:8000
- **Dokumentacja (Swagger)**: http://localhost:8000/docs
- **Alternatywna dokumentacja (ReDoc)**: http://localhost:8000/redoc

## 📊 Struktura bazy danych

### Tabele:

1. **users** - użytkownicy (wolontariusze, organizacje, koordynatorzy)
2. **initiatives** - inicjatywy wolontariackie
3. **participations** - uczestnictwa w inicjatywach
4. **certificates** - zaświadczenia o wolontariacie

## 🔌 Endpointy API

### Ogólne

- `GET /` - Informacje o API
- `GET /users` - Lista użytkowników
- `GET /users/{user_id}` - Szczegóły użytkownika
- `GET /statistics` - Statystyki platformy

### Inicjatywy

- `GET /initiatives` - Lista inicjatyw (z filtrowaniem)
  - Parametry: `category`, `location`, `status`, `organization_id`
- `GET /initiatives/{id}` - Szczegóły inicjatywy
- `POST /initiatives` - Utwórz inicjatywę (organizacja)
- `POST /initiatives/{id}/apply` - Zgłoś się do inicjatywy (wolontariusz)

### Wolontariusze

- `GET /volunteers/{id}/participations` - Uczestnictwa wolontariusza
- `GET /volunteers/{id}/certificates` - Zaświadczenia wolontariusza

### Organizacje

- `GET /organizations/{id}/initiatives` - Inicjatywy organizacji
- `GET /organizations/{id}/applications` - Zgłoszenia do inicjatyw
- `PUT /participations/{id}/approve` - Zatwierdź/odrzuć zgłoszenie

### Zaświadczenia

- `POST /certificates` - Wygeneruj zaświadczenie

### Koordynatorzy

- `GET /coordinators/{id}/students` - Lista uczniów
- `GET /coordinators/{id}/reports` - Raporty szkolne

## 🧪 Przykładowe dane testowe

### Użytkownicy (przykłady):

**Wolontariusze:**
- ID: 1 - Anna Kowalska (anna.kowalska@student.krakow.pl)
- ID: 2 - Jan Nowak (jan.nowak@student.krakow.pl)
- ID: 7 - Agnieszka Szymańska (agnieszka.szymanska@gmail.com) - pełnoletnia

**Organizacje:**
- ID: 11 - Fundacja Pomocna Dłoń
- ID: 12 - Krakowskie Centrum Kultury
- ID: 13 - Schronisko dla Zwierząt w Krakowie

**Koordynatorzy:**
- ID: 18 - Beata Nowacka (Szkoła ID: 1)
- ID: 19 - Marek Kowalczyk (Szkoła ID: 2)

### Przykładowe inicjatywy:

1. Sprzątanie Parku Jordana (Ekologia)
2. Pomoc w organizacji Festiwalu Kultury (Kultura)
3. Opieka nad zwierzętami w schronisku (Opieka nad zwierzętami)
4. Zbiórka żywności dla potrzebujących (Pomoc społeczna)

## 📝 Przykłady użycia API

### Pobierz wszystkie inicjatywy ekologiczne

```bash
curl "http://localhost:8000/initiatives?category=Ekologia"
```

### Zgłoś się do inicjatywy (wolontariusz ID: 1, inicjatywa ID: 5)

```bash
curl -X POST "http://localhost:8000/initiatives/5/apply" \
  -H "Content-Type: application/json" \
  -d '{
    "volunteer_id": 1,
    "initiative_id": 5,
    "message": "Chętnie pomogę!"
  }'
```

### Utwórz nową inicjatywę (organizacja ID: 11)

```bash
curl -X POST "http://localhost:8000/initiatives" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Warsztaty fotograficzne",
    "description": "Nauka podstaw fotografii dla młodzieży",
    "category": "Edukacja",
    "location": "Kazimierz",
    "start_date": "2025-11-01",
    "end_date": "2025-11-03",
    "hours_required": 6,
    "spots_available": 15,
    "requirements": "Własny aparat lub smartfon",
    "organization_id": 11
  }'
```

### Zatwierdź zgłoszenie wolontariusza (uczestnictwo ID: 1)

```bash
curl -X PUT "http://localhost:8000/participations/1/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved"
  }'
```

### Wygeneruj zaświadczenie

```bash
curl -X POST "http://localhost:8000/certificates" \
  -H "Content-Type: application/json" \
  -d '{
    "participation_id": 1,
    "organization_id": 11
  }'
```

### Pobierz statystyki platformy

```bash
curl "http://localhost:8000/statistics"
```

## 🎯 Funkcjonalności

### 1. Przeglądanie inicjatyw
- Filtrowanie po kategorii, lokalizacji, statusie
- Szczegółowe informacje o każdej inicjatywie

### 2. Zarządzanie zgłoszeniami
- Wolontariusze mogą zgłaszać się jednym kliknięciem
- Organizacje widzą wszystkie zgłoszenia
- System statusów: pending → approved → completed

### 3. Zaświadczenia
- Automatyczne generowanie po zakończeniu wolontariatu
- Zapis wszystkich szczegółów (godziny, data, organizacja)

### 4. Raporty dla koordynatorów
- Statystyki uczniów danej szkoły
- Najpopularniejsze kategorie
- Łączna liczba godzin wolontariatu

### 5. Mapa inicjatyw
- Każda inicjatywa ma współrzędne geograficzne
- Dane gotowe do wizualizacji na mapie


## 📦 Pliki projektu

```
├── main.py                 # Główny plik aplikacji FastAPI
├── init_database.py        # Skrypt inicjalizujący bazę danych
├── requirements.txt        # Zależności Python
├── README.md              # Ten plik
└── volunteer.db           # Baza danych SQLite (generowana)
```

## 🛠️ Technologie

- **FastAPI** - nowoczesny framework webowy Python
- **SQLite** - lekka baza danych
- **Pydantic** - walidacja danych
- **Uvicorn** - serwer ASGI

## 📞 Przykładowe przypadki użycia

### Scenariusz 1: Wolontariusz szuka inicjatywy

1. Otwórz: http://localhost:8000/docs
2. Użyj endpointu `GET /initiatives?category=Ekologia`
3. Wybierz inicjatywę i sprawdź szczegóły: `GET /initiatives/{id}`
4. Zgłoś się: `POST /initiatives/{id}/apply` z `volunteer_id: 1`

### Scenariusz 2: Organizacja zarządza inicjatywą

1. Zobacz inicjatywy organizacji: `GET /organizations/11/initiatives`
2. Zobacz zgłoszenia: `GET /organizations/11/applications`
3. Zatwierdź wolontariusza: `PUT /participations/{id}/approve`
4. Po zakończeniu ustaw status na "completed"
5. Wygeneruj zaświadczenie: `POST /certificates`

### Scenariusz 3: Koordynator monitoruje uczniów

1. Zobacz listę uczniów: `GET /coordinators/18/students`
2. Wygeneruj raport: `GET /coordinators/18/reports`
3. Zobacz statystyki platformy: `GET /statistics`

## 🎨 Kategorie inicjatyw

- Pomoc społeczna
- Ekologia
- Kultura
- Edukacja
- Sport
- Opieka nad zwierzętami
- Pomoc seniorom

## 📍 Lokalizacje w Krakowie

- Stare Miasto
- Kazimierz
- Podgórze
- Krowodrza
- Nowa Huta
- Dębniki
- Prądnik Biały

---

**Powodzenia w prezentacji projektu przed jury!** 🎉
