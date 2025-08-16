# Napisz program, który ułatwi milionom Polaków śledzenie własnych wydatków oraz ich analizę. Program pozwala na łatwe dodawanie nowych wydatków i generowanie raportów. Aplikacja działa także pomiędzy uruchomieniami, przechowując wszystkie dane w pliku. Każdy wydatek ma id, opis oraz wielkość kwoty.

## 1. Program posiada podkomendy add, report, export-python oraz import-csv. 

## 2. Podkomenda add pozwala na dodanie nowego wydatku. Należy wówczas podać jako kolejne argumenty wiersza poleceń wielkość wydatku (jako int) oraz jego opis (w cudzysłowach). Na przykład:
# $ python budget.py add 100 "stówa na zakupy". 
# Jako id wybierz pierwszy wolny id - np. jeśli masz już wydatki z id = 1, 2, 4, 5, wówczas wybierz id = 3.

## 3. Podkomenda report wyświetla wszystkie wydatki w tabeli. W tabeli znajduje się także kolumna "big?", w której znajduje się ptaszek, gdy wydatek jest duży, tzn. co najmniej 1000. Dodatkowo, na samym końcu wyświetlona jest suma wszystkich wydatów.

## 4. Podkomenda export-python wyświetla listę wszystkich wydatków jako obiekt (hint: zaimplementuj poprawnie metodę __repr__ w klasie reprezentującej pojedynczy wydatek).

## 5. Podkomenda import-csv importuję listę wydatków z pliku CSV.

## 6. Program przechowuje pomiędzy uruchomieniami bazę wszystkich wydatków w pliku budget.db. Zapisuj i wczytuj stan używając modułu pickle. Jeżeli plik nie istnieje, to automatycznie stwórz nową, pustą bazę. Zauważ, że nie potrzebujemy podpolecenia init.

## 7. Wielkość wydatku musi być dodatnią liczbą. Gdzie umieścisz kod sprawdzający, czy jest to spełnione? W jaki sposób zgłosisz, że warunek nie jest spełniony?


# Ćwiczenie: migracja przechowywania wydatków z pickle -> SQLite.


## Nowa baza (SQLite): `data/budget.sqlite3`.

## Instalacja i uruchomienie
```bash
git clone <URL repozytorium>
cd budget_sqlite
pip install click
```

## Przykłady użycia
```bash
python M07_projekt.py add 100 "zakupy spożywcze"
python M07_projekt.py add 1500 "laptop"
python M07_projekt.py report
python M07_projekt.py export-python
python M07_projekt.py import-csv dane.csv
python M07_projekt.py migrate-to-sqlite
```

## Domyślnie używany jest SQLite. Możesz wskazać backend explicite:
```bash
python M07_projekt.py --backend sqlite report
python M07_projekt.py --backend mysql add 100 "nowy laptop"
```

### Output przykładowego report:
```txt
--ID-- -AMOUNT- -BIG?- --DESCRIPTION----
   1     100.00        zakupy spożywcze
   2    1500.00  (!)   laptop
Total= 1600.0
```

## Różnice względem wersji pickle
- Poprzednia wersja używała modułu pickle do przechowywania danych w pliku budget.db

- Obecna wersja używa SQLite (data/budget.sqlite3)

- Dodano jednorazową komendę migrate-to-sqlite do migracji istniejących danych z pickle

## Jak zobaczyć zawartość bazy budget.sqlite3

1. W terminalu (Python):
```bash
import sqlite3

conn = sqlite3.connect("data/budget.sqlite3")
cursor = conn.cursor()
cursor.execute("SELECT * FROM expenses")
print(cursor.fetchall())
conn.close()
```

2. Przez wbudowane narzędzie sqlite3 w konsoli:
```bash
sqlite3 data/budget.sqlite3
sqlite> .tables
sqlite> SELECT * FROM expenses;
sqlite> .quit
```