import sqlite3
from datetime import datetime


def init_db():
    """tworzy baze 'cyber_trener.db' i tabelę historia_treningow"""
    conn = sqlite3.connect('cyber_trener.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historia_treningow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uzytkownik TEXT,
            data_treningu TIMESTAMP,
            typ_bledu TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ System bazy danych zainicjowany.")


def log_error(uzytkownik, typ_bledu):
    """zapisuje blad treningowy do bazy danych"""
    conn = sqlite3.connect('cyber_trener.db')
    cursor = conn.cursor()
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO historia_treningow (uzytkownik, data_treningu, typ_bledu)
        VALUES (?, ?, ?)
    ''', (uzytkownik, teraz, typ_bledu))

    conn.commit()
    conn.close()
    print(f"📝 [LOG] Zapisano błąd: '{typ_bledu}' dla użytkownika {uzytkownik}")


def get_history(uzytkownik):
    """pobiera i zwraca historie bledow dla uzytkownika."""
    conn = sqlite3.connect('cyber_trener.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT data_treningu, typ_bledu 
        FROM historia_treningow 
        WHERE uzytkownik = ? 
        ORDER BY data_treningu DESC
    ''', (uzytkownik,))

    wyniki = cursor.fetchall()
    conn.close()
    return wyniki


#test
if __name__ == "__main__":
    print("--- URUCHAMIANIE TESTÓW MODUŁU BAZY DANYCH ---")

    init_db()

    print("\nSymulacja treningu...")
    log_error("Student_Zaliczenie", "Zbyt proste kolana")
    log_error("Student_Zaliczenie", "Zbyt mocno ugięte łokcie")
    log_error("Student_Zaliczenie", "Brak poprawnej postawy startowej")

    print("\n--- HISTORIA TRENINGÓW ---")
    historia = get_history("Student_Zaliczenie")

    if historia:
        for data, blad in historia:
            print(f"[{data}] Błąd: {blad}")
    else:
        print("Brak historii dla tego użytkownika.")

    print("\n✅ Testy zakończone sukcesem. Moduł jest gotowy do integracji z kamerami.")