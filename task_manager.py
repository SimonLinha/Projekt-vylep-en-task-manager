# task_manager.py
# 🧭 Správce úkolů s MySQL databází
# -------------------------------
# Před spuštěním:
# 1️⃣ Ujisti se, že MySQL běží: brew services start mysql
# 2️⃣ Vytvoř databázi v MySQL: CREATE DATABASE task_manager;
# 3️⃣ Nainstaluj knihovnu: pip install mysql-connector-python
# 4️⃣ Změň heslo níže na své root heslo

import os
import mysql.connector
from mysql.connector import Error

# ==============================
# 1️⃣ Připojení k databázi
# ==============================
def pripojeni_db():
    """
    Připojí se k MySQL databázi.
    Název databáze se bere z proměnné prostředí DB_NAME (jinak použije 'task_manager').
    """
    try:
        spojeni = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),            # host – většinou localhost
            user=os.getenv("DB_USER", "root"),                 # uživatelské jméno
            password=os.getenv("DB_PASSWORD", "MojeNoveHeslo123!"),  # tvoje MySQL heslo
            database=os.getenv("DB_NAME", "task_manager")      # pokud není nastavena proměnná DB_NAME, použije task_manager
        )
        return spojeni
    except Error as e:
        print("Chyba při připojení k databázi:", e)
        return None


# ==============================
# 2️⃣ Vytvoření tabulky, pokud neexistuje
# ==============================
def vytvoreni_tabulky():
    spojeni = pripojeni_db()
    if spojeni:
        cursor = spojeni.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT NOT NULL,
            stav ENUM('nezahájeno','probíhá','hotovo') DEFAULT 'nezahájeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        spojeni.commit()
        cursor.close()
        spojeni.close()

# ==============================
# 3️⃣ Přidání úkolu
# ==============================
def pridat_ukol(nazev: str, popis: str) -> bool:
    nazev = nazev.strip()
    popis = popis.strip()
    if not nazev or not popis:
        return False

    spojeni = pripojeni_db()
    if spojeni:
        cursor = spojeni.cursor()
        sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
        cursor.execute(sql, (nazev, popis))
        spojeni.commit()
        cursor.close()
        spojeni.close()
        return True
    return False

# ==============================
# 4️⃣ Zobrazení úkolů
# ==============================
def zobraz_ukoly():
    spojeni = pripojeni_db()
    if spojeni:
        cursor = spojeni.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ukoly WHERE stav IN ('nezahájeno','probíhá')")
        vysledek = cursor.fetchall()
        if not vysledek:
            print("Žádné úkoly nejsou zadány.")
        else:
            print("\n📋 Seznam úkolů:")
            print("-" * 50)
            for ukol in vysledek:
                print(f"ID: {ukol['id']} | Název: {ukol['nazev']} | Popis: {ukol['popis']} | Stav: {ukol['stav']}")
        cursor.close()
        spojeni.close()

# ==============================
# 5️⃣ Aktualizace stavu úkolu
# ==============================
def aktualizovat_ukol(id_ukolu: int, novy_stav: str) -> bool:
    if novy_stav not in ('probíhá','hotovo'):
        return False

    spojeni = pripojeni_db()
    if spojeni:
        cursor = spojeni.cursor()
        cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
        spojeni.commit()
        updated = cursor.rowcount
        cursor.close()
        spojeni.close()
        return updated > 0
    return False

# ==============================
# 6️⃣ Odstranění úkolu
# ==============================
def odstranit_ukol(id_ukolu: int) -> bool:
    spojeni = pripojeni_db()
    if spojeni:
        cursor = spojeni.cursor()
        cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
        spojeni.commit()
        deleted = cursor.rowcount
        cursor.close()
        spojeni.close()
        return deleted > 0
    return False

# ==============================
# 7️⃣ Hlavní menu programu
# ==============================
def hlavni_menu():
    vytvoreni_tabulky()  # vytvoří tabulku při startu
    while True:
        print("\n========== Správce úkolů ==========")
        print("1. ➕ Přidat nový úkol")
        print("2. 📋 Zobrazit všechny úkoly")
        print("3. 🔄 Aktualizovat stav úkolu")
        print("4. ❌ Odstranit úkol")
        print("5. 🚪 Konec programu")

        try:
            moznost = int(input("Vyberte možnost (1-5): "))
        except ValueError:
            print("❌ Zadejte platné číslo.")
            continue

        if moznost == 1:
            nazev = input("Zadejte název úkolu: ").strip()
            popis = input("Zadejte popis úkolu: ").strip()
            if pridat_ukol(nazev, popis):
                print("✅ Úkol byl úspěšně přidán.")
            else:
                print("❌ Název i popis musí být vyplněny.")

        elif moznost == 2:
            zobraz_ukoly()

        elif moznost == 3:
            # 👇 ZDE je oprava – zobrazíme seznam úkolů před aktualizací
            zobraz_ukoly()

            try:
                id_ukolu = int(input("\nZadejte ID úkolu, jehož stav chcete změnit: "))
                novy_stav = input("Zadejte nový stav (probíhá/hotovo): ").strip().lower()
                if aktualizovat_ukol(id_ukolu, novy_stav):
                    print("✅ Úkol byl úspěšně aktualizován.")
                else:
                    print("❌ Neplatné ID nebo stav.")
            except ValueError:
                print("❌ Zadejte platné číslo ID.")

        elif moznost == 4:
            zobraz_ukoly()
            try:
                id_ukolu = int(input("\nZadejte ID úkolu k odstranění: "))
                if odstranit_ukol(id_ukolu):
                    print("🗑️ Úkol byl odstraněn.")
                else:
                    print("❌ Neplatné ID.")
            except ValueError:
                print("❌ Zadejte platné číslo.")

        elif moznost == 5:
            print("👋 Ukončuji program...")
            break

        else:
            print("❌ Neplatná volba. Zkuste to znovu.")

# ==============================
# 8️⃣ Spuštění programu
# ==============================
if __name__ == "__main__":
    hlavni_menu()
