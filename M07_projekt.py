from dataclasses import dataclass
from typing import List, Dict
import csv
import pickle
import sys

import click

BIG_EXPENSE = 1000

DB_FILENAME = 'budget.db'


@dataclass
class Expense:
    id: int
    amount: float
    description: str
    
    def __post_init__(self):
        if self.amount <= 0:   
            raise ValueError ("Amount cannot be negative or zero value.")
    

    def is_big(self) -> bool:
        return self.amount >= BIG_EXPENSE
    

    def __repr__(self) -> str:
        return f"Expense(id={self.id}, amount={self.amount:.2f}, description={self.description!r})"


def find_next_id(expenses: List[Expense]):
    ids = {expense.id for expense in expenses}
    counter = 1
    while counter in ids:
        counter += 1
    return counter


def read_or_init_budget() -> List[Expense]:
    try:
        with open(DB_FILENAME, 'rb') as stream:
            expenses = pickle.load(stream)
    except FileNotFoundError:
        expenses = []
    return expenses


def save_budget(expenses: List[Expense], overwrite: bool=True) -> None:
    if overwrite:
        mode = 'wb'
    else:
        mode = 'xb'
    with open(DB_FILENAME, mode) as stream:
        pickle.dump(expenses, stream)


def total_expenses(expenses: List[Expense]) -> float:
    return sum(expense.amount for expense in expenses)


def print_expenses(expenses: List[Expense]) -> None:
    if expenses:    
        print(f"--ID-- -AMOUNT- -BIG?- --DESCRIPTION----")
        for expense in expenses:
            if expense.is_big():
                big = '(!)'
            else:
                big = ''
            print(f"{expense.id:4} {expense.amount:10.2f} {big:^6} {expense.description}")

        total = total_expenses(expenses)    
        print(f'Total= {total}')   
    else:
        print("Nie wprowadziłeś jeszcze żadnego wydatku")


def add_expense(amount: float, description: str, expenses: List[Expense]) -> None:
    expense = Expense(
        id=find_next_id(expenses),
        amount=amount,
        description=description,
    )
    expenses.append(expense)
    

@click.group()
def cli():
    pass

@cli.command()
@click.argument('amount', type=float)
@click.argument('description')
def add(amount: float, description: str):
    try:
        expenses = read_or_init_budget()
        add_expense(amount, description, expenses)
        save_budget(expenses)
        print(":-)) SUCCESS")
    except ValueError as e:
        print(f'Błąd: {e.args[0]}')
        sys.exit(1)


@cli.command()
def report():
    expenses = read_or_init_budget()
    print_expenses(expenses)


@cli.command()
@click.argument('csv_file')
def import_csv(csv_file: str) -> None:
    expenses = read_or_init_budget()

    try:
        with open(csv_file, encoding='utf-8') as stream:
            reader = csv.DictReader(stream)
            for row in reader:
                expense = Expense(
                    id=find_next_id(expenses),
                    amount=float(row['amount']),
                    description=row['description'],
                )
                expenses.append(expense)    
    except Exception as e:
        print(f"Błąd importu: {e.args[0]}")
        sys.exit(1)

    save_budget(expenses)
    print(":-) zaimportowano")


@cli.command()
def export_python():
    expenses = read_or_init_budget()
    for expense in expenses:
        print(repr(expense))


if __name__ == "__main__":
    cli()
