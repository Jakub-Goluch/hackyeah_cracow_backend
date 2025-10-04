import sqlite3
from datetime import datetime, timedelta
import random


def create_database():
    """Utwórz schemat bazy danych"""
    conn = sqlite3.connect('volunteer.db')
    cursor = conn.cursor()

    # Tabela użytkowników
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            user_type TEXT NOT NULL CHECK(user_type IN ('volunteer', 'organization', 'coordinator')),
            age_category TEXT CHECK(age_category IN ('minor', 'adult', NULL)),
            school_id INTEGER,
            organization_type TEXT,
            address TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela inicjatyw
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS initiatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            location TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            hours_required INTEGER NOT NULL,
            spots_available INTEGER NOT NULL,
            requirements TEXT,
            organization_id INTEGER NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'cancelled')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organization_id) REFERENCES users(id)
        )
    """)

    # Tabela uczestnictw
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer_id INTEGER NOT NULL,
            initiative_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected', 'completed')),
            applied_date TIMESTAMP NOT NULL,
            approved_date TIMESTAMP,
            hours_completed INTEGER DEFAULT 0,
            message TEXT,
            feedback TEXT,
            FOREIGN KEY (volunteer_id) REFERENCES users(id),
            FOREIGN KEY (initiative_id) REFERENCES initiatives(id),
            UNIQUE(volunteer_id, initiative_id)
        )
    """)

    # Tabela zaświadczeń
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participation_id INTEGER NOT NULL,
            volunteer_id INTEGER NOT NULL,
            organization_id INTEGER NOT NULL,
            issued_date TIMESTAMP NOT NULL,
            hours_completed INTEGER NOT NULL,
            certificate_data TEXT,
            FOREIGN KEY (participation_id) REFERENCES participations(id),
            FOREIGN KEY (volunteer_id) REFERENCES users(id),
            FOREIGN KEY (organization_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    print("✓ Schemat bazy danych utworzony")
    return conn


def populate_test_data(conn):
    """Wypełnij bazę danymi testowymi"""
    cursor = conn.cursor()

    # === UŻYTKOWNICY ===

    # Wolontariusze
    volunteers = [
        ("Anna Kowalska", "anna.kowalska@student.krakow.pl", "123456789", "volunteer", "minor", 1),
        ("Jan Nowak", "jan.nowak@student.krakow.pl", "234567890", "volunteer", "minor", 1),
        ("Maria Wiśniewska", "maria.wisniewska@student.krakow.pl", "345678901", "volunteer", "adult", 2),
        ("Piotr Lewandowski", "piotr.lewandowski@student.krakow.pl", "456789012", "volunteer", "adult", 2),
        ("Katarzyna Dąbrowska", "katarzyna.dabrowska@student.krakow.pl", "567890123", "volunteer", "minor", 3),
        ("Tomasz Zieliński", "tomasz.zielinski@student.krakow.pl", "678901234", "volunteer", "minor", 3),
        ("Agnieszka Szymańska", "agnieszka.szymanska@gmail.com", "789012345", "volunteer", "adult", None),
        ("Michał Woźniak", "michal.wozniak@gmail.com", "890123456", "volunteer", "adult", None),
        ("Ewa Kozłowska", "ewa.kozlowska@student.krakow.pl", "901234567", "volunteer", "minor", 1),
        ("Paweł Jankowski", "pawel.jankowski@student.krakow.pl", "012345678", "volunteer", "minor", 2),
    ]

    for v in volunteers:
        cursor.execute("""
            INSERT INTO users (name, email, phone, user_type, age_category, school_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, v)

    print(f"✓ Dodano {len(volunteers)} wolontariuszy")

    # Organizacje
    organizations = [
        ("Fundacja Pomocna Dłoń", "kontakt@pomocnadlon.org.pl", "122223344",
         "organization", None, None, "NGO", "ul. Floriańska 10, Kraków",
         "Fundacja zajmująca się pomocą potrzebującym i organizacją wolontariatów społecznych."),

        ("Krakowskie Centrum Kultury", "biuro@kck.krakow.pl", "123334455",
         "organization", None, None, "Instytucja kultury", "ul. Grodzka 25, Kraków",
         "Miejska instytucja kultury promująca sztukę i kulturę w Krakowie."),

        ("Schronisko dla Zwierząt w Krakowie", "info@schronisko.krakow.pl", "124445566",
         "organization", None, None, "NGO", "ul. Rybna 6, Kraków",
         "Schronisko dbające o bezdomne zwierzęta i promujące adopcje."),

        ("Zielony Kraków - Fundacja Ekologiczna", "zielony@krakow.org.pl", "125556677",
         "organization", None, None, "NGO", "ul. Dietla 30, Kraków",
         "Organizacja zajmująca się ekologią i ochroną środowiska w Krakowie."),

        ("Muzeum Narodowe w Krakowie", "edukacja@mnk.pl", "126667788",
         "organization", None, None, "Instytucja kultury", "al. 3 Maja 1, Kraków",
         "Jedno z najstarszych muzeów w Polsce, oferujące programy edukacyjne."),

        ("Krakowski Bank Żywności", "kontakt@bankzywnosci.krakow.pl", "127778899",
         "organization", None, None, "NGO", "ul. Zakopiańska 56, Kraków",
         "Organizacja walcząca z marnotrawstwem żywności i pomagająca potrzebującym."),

        ("Fundacja Seniorzy w Akcji", "biuro@seniorzy.krakow.pl", "128889900",
         "organization", None, None, "NGO", "ul. Starowiślna 13, Kraków",
         "Fundacja wspierająca seniorów i organizująca integrację międzypokoleniową."),
    ]

    for org in organizations:
        cursor.execute("""
            INSERT INTO users (name, email, phone, user_type, age_category, school_id, 
                             organization_type, address, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, org)

    print(f"✓ Dodano {len(organizations)} organizacji")

    # Koordynatorzy szkolni
    coordinators = [
        ("Beata Nowacka", "b.nowacka@liceum1.krakow.pl", "601234567", "coordinator", None, 1),
        ("Marek Kowalczyk", "m.kowalczyk@gimnazjum2.krakow.pl", "602345678", "coordinator", None, 2),
        ("Joanna Wiśniewska", "j.wisniewska@zstech3.krakow.pl", "603456789", "coordinator", None, 3),
    ]

    for coord in coordinators:
        cursor.execute("""
            INSERT INTO users (name, email, phone, user_type, age_category, school_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, coord)

    print(f"✓ Dodano {len(coordinators)} koordynatorów")

    # === INICJATYWY ===

    categories = ["Pomoc społeczna", "Ekologia", "Kultura", "Edukacja", "Sport",
                  "Opieka nad zwierzętami", "Pomoc seniorom"]

    locations = [
        ("Stare Miasto", 50.0614, 19.9372),
        ("Kazimierz", 50.0519, 19.9464),
        ("Podgórze", 50.0345, 19.9495),
        ("Krowodrza", 50.0836, 19.9155),
        ("Nowa Huta", 50.0705, 20.0340),
        ("Dębniki", 50.0431, 19.9053),
        ("Prądnik Biały", 50.0957, 19.9395),
    ]

    initiatives_data = [
        ("Sprzątanie Parku Jordana",
         "Pomoc w wiosennym sprzątaniu parku, sadzeniu kwiatów i przygotowaniu terenu na sezon letni.",
         "Ekologia", 4, 15, "Chęć do pracy na świeżym powietrzu, odpowiedni ubiór"),

        ("Pomoc w organizacji Festiwalu Kultury",
         "Wsparcie przy organizacji miejskiego festiwalu - obsługa stoisk, pomoc techniczna, opieka nad gośćmi.",
         "Kultura", 6, 20, "Komunikatywność, znajomość języka angielskiego mile widziana"),

        ("Opieka nad zwierzętami w schronisku",
         "Codzienne spacery z psami, pomoc przy karmieniu i sprzątaniu, socjalizacja zwierząt.",
         "Opieka nad zwierzętami", 3, 8, "Brak lęku przed zwierzętami, odpowiedzialność"),

        ("Zbiórka żywności dla potrzebujących",
         "Pomoc przy organizacji zbiórki żywności w supermarketach, sortowanie i pakowanie darów.",
         "Pomoc społeczna", 4, 12, "Punktualność, umiejętność pracy w zespole"),

        ("Warsztaty edukacyjne dla dzieci",
         "Prowadzenie kreatywnych warsztatów dla dzieci z przedszkoli - rysowanie, zabawy edukacyjne.",
         "Edukacja", 5, 6, "Doświadczenie w pracy z dziećmi, kreatywność"),

        ("Sadzenie drzew w Lesie Wolskim",
         "Udział w akcji sadzenia drzew, przygotowanie terenu, pielęgnacja młodych nasadzeń.",
         "Ekologia", 6, 25, "Dobra kondycja fizyczna, gotowość do pracy fizycznej"),

        ("Pomoc seniorom w korzystaniu z technologii",
         "Nauka obsługi smartfonów i komputerów dla seniorów, pomoc w załatwianiu spraw online.",
         "Pomoc seniorom", 2, 10, "Cierpliwość, umiejętność jasnego przekazywania informacji"),

        ("Nocne czuwanie w muzeum",
         "Udział w wydarzeniu Noc Muzeów - prowadzenie zwiedzających, asystowanie przy eksponatach.",
         "Kultura", 8, 15, "Zainteresowanie historią sztuki, dyspozycyjność wieczorem"),

        ("Turniej sportowy dla młodzieży",
         "Pomoc w organizacji miejskiego turnieju piłki nożnej - rejestracja, sędziowanie, obsługa.",
         "Sport", 10, 12, "Znajomość zasad gry, doświadczenie sportowe mile widziane"),

        ("Renowacja alejek w Parku Krakowskim",
         "Pomoc przy odnawianiu ławek, malowaniu, naprawie alejek parkowych.",
         "Ekologia", 5, 10, "Umiejętności manualne, dokładność"),

        ("Festyn rodzinny - animacje dla dzieci",
         "Animowanie zabaw dla dzieci podczas festynu rodzinnego, malowanie twarzy, konkursy.",
         "Kultura", 6, 8, "Umiejętność pracy z dziećmi, energia, kreatywność"),

        ("Kampania adopcyjna zwierząt",
         "Pomoc w organizacji weekendowej kampanii adopcyjnej - prezentacja zwierząt, rozdawanie ulotek.",
         "Opieka nad zwierzętami", 4, 6, "Komunikatywność, zaangażowanie w sprawę"),

        ("Lekcje języka polskiego dla obcokrajowców",
         "Prowadzenie konwersacji w języku polskim z imigrantami i uchodźcami.",
         "Edukacja", 3, 5, "Cierpliwość, umiejętność dydaktyczne"),

        ("Sprzątanie brzegów Wisły",
         "Ekologiczna akcja sprzątania brzegów Wisły z plastiku i śmieci.",
         "Ekologia", 4, 30, "Rękawice ochronne zapewnione, chęć do pracy fizycznej"),

        ("Pomoc w bibliotece miejskiej",
         "Katalogowanie książek, pomoc czytelnikom, organizacja wydarzeń czytelniczych.",
         "Kultura", 3, 4, "Zamiłowanie do czytania, dokładność"),
    ]

    org_ids = list(range(11, 18))  # IDs organizacji (11-17)

    for i, (title, desc, category, hours, spots, reqs) in enumerate(initiatives_data):
        org_id = random.choice(org_ids)
        location_name, lat, lon = random.choice(locations)

        start_date = datetime.now() + timedelta(days=random.randint(5, 60))
        end_date = start_date + timedelta(days=random.randint(1, 14))

        cursor.execute("""
            INSERT INTO initiatives 
            (title, description, category, location, latitude, longitude,
             start_date, end_date, hours_required, spots_available, 
             requirements, organization_id, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, desc, category, location_name, lat, lon,
              start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"),
              hours, spots, reqs, org_id, 'active'))

    print(f"✓ Dodano {len(initiatives_data)} inicjatyw")

    # === UCZESTNICTWA ===

    volunteer_ids = list(range(1, 11))  # IDs wolontariuszy (1-10)
    initiative_ids = list(range(1, 16))  # IDs inicjatyw (1-15)

    participations_count = 0
    for _ in range(30):  # 30 przykładowych uczestnictw
        volunteer_id = random.choice(volunteer_ids)
        initiative_id = random.choice(initiative_ids)

        # Sprawdź czy już nie istnieje
        cursor.execute("""
            SELECT id FROM participations 
            WHERE volunteer_id = ? AND initiative_id = ?
        """, (volunteer_id, initiative_id))

        if cursor.fetchone():
            continue

        status = random.choices(
            ['pending', 'approved', 'completed', 'rejected'],
            weights=[30, 40, 25, 5]
        )[0]

        applied_date = datetime.now() - timedelta(days=random.randint(1, 30))
        approved_date = None
        hours_completed = 0

        if status in ['approved', 'completed']:
            approved_date = applied_date + timedelta(days=random.randint(1, 3))

        if status == 'completed':
            hours_completed = random.randint(2, 8)

        cursor.execute("""
            INSERT INTO participations 
            (volunteer_id, initiative_id, status, applied_date, 
             approved_date, hours_completed, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (volunteer_id, initiative_id, status,
              applied_date.isoformat(),
              approved_date.isoformat() if approved_date else None,
              hours_completed,
              "Chętnie pomogę w tej inicjatywie!" if random.random() > 0.5 else None))

        participations_count += 1

    print(f"✓ Dodano {participations_count} uczestnictw")

    # === ZAŚWIADCZENIA ===

    # Pobierz ukończone uczestnictwa
    cursor.execute("""
        SELECT p.id, p.volunteer_id, i.organization_id, p.hours_completed
        FROM participations p
        JOIN initiatives i ON p.initiative_id = i.id
        WHERE p.status = 'completed'
        LIMIT 10
    """)

    completed = cursor.fetchall()

    for participation in completed:
        part_id, vol_id, org_id, hours = participation

        issued_date = datetime.now() - timedelta(days=random.randint(1, 20))

        cursor.execute("""
            INSERT INTO certificates 
            (participation_id, volunteer_id, organization_id, 
             issued_date, hours_completed, certificate_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (part_id, vol_id, org_id, issued_date.isoformat(),
              hours, '{"type": "volunteer_certificate"}'))

    print(f"✓ Dodano {len(completed)} zaświadczeń")

    conn.commit()
    print("\n✓ Baza danych wypełniona danymi testowymi!")


def main():
    print("=== Inicjalizacja bazy danych ===\n")

    # Usuń starą bazę jeśli istnieje
    import os
    if os.path.exists('volunteer.db'):
        os.remove('volunteer.db')
        print("✓ Usunięto starą bazę danych")

    # Utwórz nową bazę
    conn = create_database()

    # Wypełnij danymi
    populate_test_data(conn)

    # Pokaż statystyki
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='volunteer'")
    volunteers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='organization'")
    organizations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE user_type='coordinator'")
    coordinators = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM initiatives")
    initiatives = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM participations")
    participations = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM certificates")
    certificates = cursor.fetchone()[0]

    print("\n=== Podsumowanie ===")
    print(f"Wolontariusze: {volunteers}")
    print(f"Organizacje: {organizations}")
    print(f"Koordynatorzy: {coordinators}")
    print(f"Inicjatywy: {initiatives}")
    print(f"Uczestnictwa: {participations}")
    print(f"Zaświadczenia: {certificates}")

    conn.close()
    print("\n✓ Gotowe! Możesz teraz uruchomić aplikację: python main.py")


if __name__ == "__main__":
    main()