from dataclasses import dataclass
from typing import List
import csv
import pickle
import sys
import os
import shutil

import click

from storage_sqlite import SQLiteStorage
from db import init_db

BIG_EXPENSE = 1000

# ---- LEGACY (tylko do migracji z pickle) ------------------------
DB_FILENAME = 'budget.db'  # stary plik z pickle (nie SQLite!)

@dataclass
class Expense:
    id: int
    amount: float
    description: str
    
    def __post_init__(self):
        if self.amount <= 0:   
            raise ValueError("Amount cannot be negative or zero value.")

    def is_big(self) -> bool:
        return self.amount >= BIG_EXPENSE

    def __repr__(self) -> str:
        return f"Expense(id={self.id}, amount={self.amount:.2f}, description={self.description!r})"

# --- Funkcje legacy oparte na pickle: użyjemy tylko w migracji ---
def read_or_init_budget() -> List[Expense]:
    try:
        with open(DB_FILENAME, 'rb') as stream:
            expenses = pickle.load(stream)
    except FileNotFoundError:
        expenses = []
    return expenses

def save_budget(expenses: List[Expense], overwrite: bool=True) -> None:
    mode = 'wb' if overwrite else 'xb'
    with open(DB_FILENAME, mode) as stream:
        pickle.dump(expenses, stream)
# -----------------------------------------------------------------

# --- Wersja na SQLite --------------------------------------------
def to_expense(row_dict) -> Expense:
    """
    Zamienia słownik z bazy (id, amount, description) na obiekt Expense.
    """
    return Expense(
        id=int(row_dict["id"]),
        amount=float(row_dict["amount"]),
        description=str(row_dict["description"])
    )

def print_expenses(expenses: List[Expense]) -> None:
    if expenses:
        print(f"--ID-- -AMOUNT- -BIG?- --DESCRIPTION----")
        for expense in expenses:
            big = '(!)' if expense.is_big() else ''
            print(f"{expense.id:4} {expense.amount:10.2f} {big:^6} {expense.description}")
        total = sum(e.amount for e in expenses)
        print(f'Total= {total}')
    else:
        print("Nie wprowadziłeś jeszcze żadnego wydatku")

@click.group()
def cli():
    """Budżet domowy: add, report, import-csv, export-python, migrate-to-sqlite"""
    # Upewniamy się, że baza istnieje.
    init_db()

@cli.command()
@click.argument('amount', type=float)
@click.argument('description')
def add(amount: float, description: str):
    """
    Dodaje nowy wydatek do bazy SQLite.
    Walidacja kwoty odbywa się w Expense.__post_init__,
    więc tworzymy tymczasowy obiekt tylko po to, by złapać ewentualny błąd.
    """
    try:
        _ = Expense(id=0, amount=amount, description=description)  # walidacja
        st = SQLiteStorage()
        new_id = st.add(amount=amount, description=description)
        print(f":-)) SUCCESS (id={new_id})")
    except ValueError as e:
        print(f'Błąd: {e.args[0]}')
        sys.exit(1)

@cli.command()
def report():
    """Wypisuje tabelę wydatków (SQLite)."""
    st = SQLiteStorage()
    rows = st.list_all()
    expenses = [to_expense(r) for r in rows]
    print_expenses(expenses)

@cli.command()
@click.argument('csv_file')
def import_csv(csv_file: str) -> None:
    """
    Import z CSV do SQLite.
    CSV powinien mieć nagłówki: amount,description
    """
    st = SQLiteStorage()
    count = 0
    try:
        with open(csv_file, encoding='utf-8') as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                amount = float(row['amount'])
                description = row['description']
                _ = Expense(id=0, amount=amount, description=description)  # walidacja
                st.add(amount=amount, description=description)
                count += 1
    except Exception as e:
        print(f"Błąd importu: {e}")
        sys.exit(1)

    print(f":-) zaimportowano {count} rekordów")

@cli.command()
def export_python():
    """
    Wypisuje listę wydatków jako repr(Expense).
    (Tak jak wcześniej, ale już z SQLite.)
    """
    st = SQLiteStorage()
    rows = st.list_all()
    for r in rows:
        print(repr(to_expense(r)))

# --- Nowa komenda: migracja z pickle -> SQLite -------------------
@cli.command(name="migrate-to-sqlite")
def migrate_to_sqlite():
    """
    Jednorazowa migracja: czyta stary plik pickle (budget.db),
    zapisuje wszystko do SQLite (data/budget.sqlite3),
    a stary plik przenosi do kopii zapasowej (budget.pkl.bak).
    """
    legacy_expenses = read_or_init_budget()

    if not legacy_expenses:
        print("Brak danych w starym pliku pickle (budget.db). Nic do migracji.")
        return

    st = SQLiteStorage()
    for e in legacy_expenses:
        # Zakładamy, że e to obiekt Expense (tak było w oryginalnej wersji)
        st.add(amount=e.amount, description=e.description)

    if os.path.exists(DB_FILENAME):
        shutil.move(DB_FILENAME, "budget.pkl.bak")

    print(f"Migracja zakończona. Przeniesiono {len(legacy_expenses)} rekordów. 🥳")
# -----------------------------------------------------------------

if __name__ == "__main__":
    cli()
