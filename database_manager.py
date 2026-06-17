import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cyber_trener.db')


def init_db():
    """Tworzy bazę 'cyber_trener.db' i tabelę historia_treningow."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historia_treningow (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            uzytkownik    TEXT,
            data_treningu TIMESTAMP,
            typ_bledu     TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ System bazy danych zainicjowany.")


def log_error(uzytkownik, typ_bledu):
    """Zapisuje błąd treningowy do bazy danych."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO historia_treningow (uzytkownik, data_treningu, typ_bledu)
        VALUES (?, ?, ?)
    ''', (uzytkownik, teraz, typ_bledu))
    conn.commit()
    conn.close()
    print(f"📝 [LOG] Błąd: '{typ_bledu}' | Użytkownik: {uzytkownik}")


def get_history(uzytkownik):
    """Zwraca historię błędów dla danego użytkownika."""
    conn = sqlite3.connect(DB_PATH)
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

if __name__ == "__main__":
    print("--- TESTY MODUŁU BAZY DANYCH ---")
    init_db()
    log_error("Student_Test", "Zbyt proste kolana")
    log_error("Student_Test", "Zbyt mocno ugięte łokcie")

    historia = get_history("Student_Test")
    for data, blad in historia:
        print(f"  [{data}] {blad}")
    print("✅ Testy zakończone.")