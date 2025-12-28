import pytest
import mysql.connector
# Importujeme všechny potřebné funkce z tvého hlavního souboru
from task_manager import pridat_ukol, aktualizovat_ukol, odstranit_ukol, pripojeni_db

# ==============================================================
# FIXTURA: Příprava testovacího prostředí
# ==============================================================
@pytest.fixture
def db_spojeni():
    """
    Tato funkce se spustí před každým testem.
    Vymaže tabulku a resetuje ID (AUTO_INCREMENT), aby testy byly předvídatelné.
    """
    conn = pripojeni_db()
    cursor = conn.cursor()
    # Vymažeme data z tabulky
    cursor.execute("DELETE FROM ukoly")
    # Resetujeme počítadlo ID na 1, aby první přidaný úkol měl vždy ID 1
    cursor.execute("ALTER TABLE ukoly AUTO_INCREMENT = 1")
    conn.commit()
    
    yield conn  # Zde se provede samotný test
    
    cursor.close()
    conn.close()

# ==============================================================
# 1. TESTY PRO: pridat_ukol()
# ==============================================================

def test_pridat_ukol_pozitivni(db_spojeni):
    """Ověří, že se správně zadaný úkol uloží do DB."""
    vysledek = pridat_ukol("Koupit mléko", "Plnotučné, 2 litry")
    assert vysledek is True

def test_pridat_ukol_negativni(db_spojeni):
    """Ověří, že prázdný název nebo popis neprojde."""
    vysledek = pridat_ukol("", "")
    assert vysledek is False

# ==============================================================
# 2. TESTY PRO: aktualizovat_ukol()
# ==============================================================

def test_aktualizovat_ukol_pozitivni(db_spojeni):
    """Ověří, že u existujícího úkolu lze změnit stav."""
    pridat_ukol("Test pro update", "Popis")
    # Protože jsme v fixtuře resetovali AUTO_INCREMENT, ID bude 1
    vysledek = aktualizovat_ukol(1, "probíhá")
    assert vysledek is True

def test_aktualizovat_ukol_negativni(db_spojeni):
    """Ověří, že nelze aktualizovat neexistující ID."""
    vysledek = aktualizovat_ukol(999, "hotovo")
    assert vysledek is False

# ==============================================================
# 3. TESTY PRO: odstranit_ukol()
# ==============================================================

def test_odstranit_ukol_pozitivni(db_spojeni):
    """Ověří, že existující úkol lze smazat."""
    pridat_ukol("Test pro smazání", "Popis")
    vysledek = odstranit_ukol(1)
    assert vysledek is True

def test_odstranit_ukol_negativni(db_spojeni):
    """Ověří, že nelze smazat ID, které v DB není."""
    vysledek = odstranit_ukol(999)
    assert vysledek is False