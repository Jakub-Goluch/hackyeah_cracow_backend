"""
Skrypt do testowania API Krakowskiego Cyfrowego Centrum Wolontariatu
Uruchom serwer przed wykonaniem testów: python main.py
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"


def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()


def test_root():
    print_section("TEST 1: Informacje o API")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)


def test_statistics():
    print_section("TEST 2: Statystyki platformy")
    response = requests.get(f"{BASE_URL}/statistics")
    print_response(response)


def test_get_initiatives():
    print_section("TEST 3: Pobierz wszystkie inicjatywy")
    response = requests.get(f"{BASE_URL}/initiatives")
    print_response(response)


def test_filter_initiatives():
    print_section("TEST 4: Filtruj inicjatywy (Ekologia)")
    response = requests.get(f"{BASE_URL}/initiatives?category=Ekologia")
    print_response(response)


def test_get_initiative_details():
    print_section("TEST 5: Szczegóły inicjatywy ID: 1")
    response = requests.get(f"{BASE_URL}/initiatives/1")
    print_response(response)


def test_get_users():
    print_section("TEST 6: Lista wszystkich użytkowników")
    response = requests.get(f"{BASE_URL}/users")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Liczba użytkowników: {data['count']}")
    print("\nPrzykładowi użytkownicy:")
    for user in data['users'][:5]:
        print(f"  - ID: {user['id']}, {user['name']} ({user['user_type']})")
    print()


def test_get_volunteers():
    print_section("TEST 7: Lista wolontariuszy")
    response = requests.get(f"{BASE_URL}/users?user_type=volunteer")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Liczba wolontariuszy: {data['count']}")
    print("\nWolontariusze:")
    for user in data['users']:
        print(f"  - ID: {user['id']}, {user['name']}, {user['age_category']}")
    print()


def test_get_organizations():
    print_section("TEST 8: Lista organizacji")
    response = requests.get(f"{BASE_URL}/users?user_type=organization")
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Liczba organizacji: {data['count']}")
    print("\nOrganizacje:")
    for user in data['users']:
        print(f"  - ID: {user['id']}, {user['name']}")
        print(f"    {user['organization_type']} - {user['address']}")
    print()


def test_volunteer_participations():
    print_section("TEST 9: Uczestnictwa wolontariusza ID: 1")
    response = requests.get(f"{BASE_URL}/volunteers/1/participations")
    print_response(response)


def test_apply_to_initiative():
    print_section("TEST 10: Zgłoszenie do inicjatywy")
    data = {
        "volunteer_id": 1,
        "initiative_id": 1,
        "message": "Bardzo chętnie wezmę udział w tym projekcie!"
    }
    response = requests.post(f"{BASE_URL}/initiatives/1/apply", json=data)
    print_response(response)


def test_create_initiative():
    print_section("TEST 11: Utworzenie nowej inicjatywy")
    start_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")

    data = {
        "title": "Warsztaty programowania dla młodzieży",
        "description": "Bezpłatne warsztaty z podstaw programowania w Python dla uczniów szkół średnich.",
        "category": "Edukacja",
        "location": "Kazimierz",
        "start_date": start_date,
        "end_date": end_date,
        "hours_required": 8,
        "spots_available": 20,
        "requirements": "Własny laptop, podstawowa znajomość obsługi komputera",
        "organization_id": 11
    }
    response = requests.post(f"{BASE_URL}/initiatives", json=data)
    print_response(response)


def test_organization_initiatives():
    print_section("TEST 12: Inicjatywy organizacji ID: 11")
    response = requests.get(f"{BASE_URL}/organizations/11/initiatives")
    print_response(response)


def test_organization_applications():
    print_section("TEST 13: Zgłoszenia do organizacji ID: 11")
    response = requests.get(f"{BASE_URL}/organizations/11/applications")
    print_response(response)


def test_approve_participation():
    print_section("TEST 14: Zatwierdzenie zgłoszenia")
    # Najpierw znajdź zgłoszenie o statusie pending
    response = requests.get(f"{BASE_URL}/organizations/11/applications?status=pending")
    applications = response.json()

    if applications['count'] > 0:
        participation_id = applications['applications'][0]['id']
        print(f"Zatwierdzam uczestnictwo ID: {participation_id}")

        data = {
            "status": "approved"
        }
        response = requests.put(f"{BASE_URL}/participations/{participation_id}/approve", json=data)
        print_response(response)
    else:
        print("Brak zgłoszeń do zatwierdzenia")


def test_complete_participation():
    print_section("TEST 15: Ukończenie wolontariatu")
    # Znajdź zatwierdzone uczestnictwo
    response = requests.get(f"{BASE_URL}/organizations/11/applications?status=approved")
    applications = response.json()

    if applications['count'] > 0:
        participation_id = applications['applications'][0]['id']
        print(f"Oznaczam jako ukończone uczestnictwo ID: {participation_id}")

        data = {
            "status": "completed",
            "hours_completed": 5
        }
        response = requests.put(f"{BASE_URL}/participations/{participation_id}/approve", json=data)
        print_response(response)
    else:
        print("Brak zatwierdzonych uczestnictw")


def test_create_certificate():
    print_section("TEST 16: Generowanie zaświadczenia")
    # Znajdź ukończone uczestnictwo
    response = requests.get(f"{BASE_URL}/organizations/11/applications?status=completed")
    applications = response.json()

    if applications['count'] > 0:
        participation_id = applications['applications'][0]['id']
        print(f"Generuję zaświadczenie dla uczestnictwa ID: {participation_id}")

        data = {
            "participation_id": participation_id,
            "organization_id": 11
        }
        response = requests.post(f"{BASE_URL}/certificates", json=data)
        print_response(response)
    else:
        print("Brak ukończonych uczestnictw")


def test_volunteer_certificates():
    print_section("TEST 17: Zaświadczenia wolontariusza")
    response = requests.get(f"{BASE_URL}/volunteers/1/certificates")
    print_response(response)


def test_coordinator_students():
    print_section("TEST 18: Uczniowie koordynatora ID: 18")
    response = requests.get(f"{BASE_URL}/coordinators/18/students")
    print_response(response)


def test_coordinator_reports():
    print_section("TEST 19: Raport koordynatora ID: 18")
    response = requests.get(f"{BASE_URL}/coordinators/18/reports")
    print_response(response)


def test_filter_by_location():
    print_section("TEST 20: Filtruj inicjatywy po lokalizacji (Kazimierz)")
    response = requests.get(f"{BASE_URL}/initiatives?location=Kazimierz")
    print_response(response)


def run_all_tests():
    print("\n" + "🚀" * 30)
    print("  TESTY API - KRAKOWSKIE CYFROWE CENTRUM WOLONTARIATU")
    print("🚀" * 30)

    try:
        # Testy podstawowe
        test_root()
        test_statistics()

        # Testy inicjatyw
        test_get_initiatives()
        test_filter_initiatives()
        test_get_initiative_details()
        test_filter_by_location()

        # Testy użytkowników
        test_get_users()
        test_get_volunteers()
        test_get_organizations()

        # Testy wolontariuszy
        test_volunteer_participations()
        test_apply_to_initiative()
        test_volunteer_certificates()

        # Testy organizacji
        test_create_initiative()
        test_organization_initiatives()
        test_organization_applications()
        test_approve_participation()
        test_complete_participation()
        test_create_certificate()

        # Testy koordynatorów
        test_coordinator_students()
        test_coordinator_reports()

        print("\n" + "✅" * 30)
        print("  WSZYSTKIE TESTY ZAKOŃCZONE")
        print("✅" * 30 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ BŁĄD: Nie można połączyć się z serwerem!")
        print("Upewnij się, że serwer działa: python main.py")
    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")


def interactive_menu():
    """Interaktywne menu do testowania poszczególnych funkcji"""
    while True:
        print("\n" + "=" * 60)
        print("  MENU TESTOWE - WYBIERZ OPCJĘ")
        print("=" * 60)
        print("1.  Informacje o API")
        print("2.  Statystyki platformy")
        print("3.  Lista wszystkich inicjatyw")
        print("4.  Filtruj inicjatywy (Ekologia)")
        print("5.  Szczegóły inicjatywy")
        print("6.  Lista użytkowników")
        print("7.  Lista wolontariuszy")
        print("8.  Lista organizacji")
        print("9.  Uczestnictwa wolontariusza")
        print("10. Zgłoś się do inicjatywy")
        print("11. Utwórz nową inicjatywę")
        print("12. Inicjatywy organizacji")
        print("13. Zgłoszenia do organizacji")
        print("14. Zatwierdź zgłoszenie")
        print("15. Ukończ wolontariat")
        print("16. Wygeneruj zaświadczenie")
        print("17. Zaświadczenia wolontariusza")
        print("18. Uczniowie koordynatora")
        print("19. Raport koordynatora")
        print("20. Filtruj po lokalizacji")
        print()
        print("A.  URUCHOM WSZYSTKIE TESTY")
        print("Q.  WYJŚCIE")
        print("=" * 60)

        choice = input("\nWybór: ").strip().upper()

        if choice == 'Q':
            print("\nDo widzenia! 👋\n")
            break
        elif choice == 'A':
            run_all_tests()
        elif choice == '1':
            test_root()
        elif choice == '2':
            test_statistics()
        elif choice == '3':
            test_get_initiatives()
        elif choice == '4':
            test_filter_initiatives()
        elif choice == '5':
            test_get_initiative_details()
        elif choice == '6':
            test_get_users()
        elif choice == '7':
            test_get_volunteers()
        elif choice == '8':
            test_get_organizations()
        elif choice == '9':
            test_volunteer_participations()
        elif choice == '10':
            test_apply_to_initiative()
        elif choice == '11':
            test_create_initiative()
        elif choice == '12':
            test_organization_initiatives()
        elif choice == '13':
            test_organization_applications()
        elif choice == '14':
            test_approve_participation()
        elif choice == '15':
            test_complete_participation()
        elif choice == '16':
            test_create_certificate()
        elif choice == '17':
            test_volunteer_certificates()
        elif choice == '18':
            test_coordinator_students()
        elif choice == '19':
            test_coordinator_reports()
        elif choice == '20':
            test_filter_by_location()
        else:
            print("❌ Nieprawidłowy wybór!")

        input("\nNaciśnij ENTER aby kontynuować...")


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  SKRYPT TESTOWY API                                          ║
    ║  Krakowskie Cyfrowe Centrum Wolontariatu                     ║
    ╚══════════════════════════════════════════════════════════════╝

    INSTRUKCJE:
    1. Upewnij się, że serwer działa (python main.py)
    2. Wybierz tryb:
       - Wciśnij 'A' aby uruchomić wszystkie testy automatycznie
       - Wciśnij 'M' aby użyć interaktywnego menu
    """)

    mode = input("Wybór (A/M): ").strip().upper()

    if mode == 'A':
        run_all_tests()
    else:
        interactive_menu()