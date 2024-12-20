import pandas as pd  # Importing pandas for data manipulation
import csv  # For working with CSV files
from datetime import datetime  # To handle date and time operations
import matplotlib.pyplot as plt  # For plotting graphs
import os  # To check file existence
from collections import defaultdict  # For managing default dictionary-like structures

# Date format to be used throughout the program
date_format = "%Y-%m-%d"
# Predefined categories for transactions: Income and Expense
CATEGORIES = {"I": "Income", "E": "Expense"}

def get_date(prompt, allow_default=False):
    date_str = input(prompt)
    if allow_default and not date_str:
        return datetime.today().strftime(date_format)

    try:
        valid_date = datetime.strptime(date_str, date_format)
        return valid_date.strftime(date_format)
    except ValueError:
        print("Invalid date format. Please enter the date in YYYY-MM-DD format.")
        return get_date(prompt, allow_default)

def get_amount():
    try:
        amount = float(input("Enter the amount: "))
        if amount <= 0:
            raise ValueError("Amount must be a positive number and not zero.")
        return amount
    except ValueError as e:
        print(e)
        return get_amount()

def get_category():
    category = input("Enter the category ('I' for Income or 'E' for Expense): ").upper()
    if category in CATEGORIES:
        return CATEGORIES[category]
    print("Invalid category. Please enter 'I' for Income or 'E' for Expense.")
    return get_category()

def get_description():
    return input("Enter a description (optional): ")

class Transaction:
    def __init__(self, date, amount, category, description):
        self.date = date
        self.amount = amount
        self.category = category
        self.description = description

class FinanceManager:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%Y-%m-%d"

    def __init__(self):
        if not os.path.exists(self.CSV_FILE):
            self.initialize_csv()
        else:
            self.sort_csv_by_date()

    def initialize_csv(self):
        df = pd.DataFrame(columns=self.COLUMNS)
        df.to_csv(self.CSV_FILE, index=False)

    def add_transaction(self, transaction):
        new_entry = {
            "date": transaction.date,
            "amount": transaction.amount,
            "category": transaction.category,
            "description": transaction.description,
        }
        with open(self.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.COLUMNS)
            writer.writerow(new_entry)
        print("Transaction added successfully!")
        self.sort_csv_by_date()

    def sort_csv_by_date(self):
        df = pd.read_csv(self.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=self.FORMAT, errors="coerce")
        if df["date"].isna().any():
            print("Some dates could not be parsed. Please check your CSV file.")
            return
        df = df.sort_values(by="date")
        df["date"] = df["date"].dt.strftime(self.FORMAT)
        df.to_csv(self.CSV_FILE, index=False)
        print("CSV file sorted by date in YYYY-MM-DD format.")

    def get_transactions(self, start_date, end_date):
        df = pd.read_csv(self.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=self.FORMAT)
        start_date = datetime.strptime(start_date, self.FORMAT)
        end_date = datetime.strptime(end_date, self.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transactions found in the given date range.")
        else:
            print(f"Transactions from {start_date.strftime(self.FORMAT)} to {end_date.strftime(self.FORMAT)}:")
            print(filtered_df.to_string(index=False, formatters={"date": lambda x: x.strftime(self.FORMAT)}))
            self._print_summary(filtered_df)

        return filtered_df

    def _print_summary(self, df):
        total_income = df[df["category"] == "Income"]["amount"].sum()
        total_expense = df[df["category"] == "Expense"]["amount"].sum()
        print("\nSummary:")
        print(f"Total Income: ${total_income:.2f}")
        print(f"Total Expense: ${total_expense:.2f}")
        print(f"Net Savings: ${(total_income - total_expense):.2f}")

    def generate_category_breakdown(self):
        df = pd.read_csv(self.CSV_FILE)
        category_summary = df[df["category"] == "Expense"]["description"].value_counts()
        print("\nCategory Breakdown:")
        print(category_summary)

    def plot_transactions(self, df):
        df["date"] = pd.to_datetime(df["date"], format=self.FORMAT)
        df.set_index("date", inplace=True)

        income_df = df[df["category"] == "Income"].resample("D").sum()
        expense_df = df[df["category"] == "Expense"].resample("D").sum()

        plt.figure(figsize=(10, 5))
        plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
        plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
        plt.xlabel("Date")
        plt.ylabel("Amount")
        plt.title("Income and Expenses Over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

def main():
    manager = FinanceManager()

    while True:
        print("\n1. Add new transaction")
        print("2. View transactions and summary within a date range")
        print("3. Generate category breakdown")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            date = get_date("Enter the date of the transaction (YYYY-MM-DD) or press Enter for today: ", allow_default=True)
            amount = get_amount()
            category = get_category()
            description = get_description()
            transaction = Transaction(date, amount, category, description)
            manager.add_transaction(transaction)

        elif choice == "2":
            start_date = get_date("Enter the start date (YYYY-MM-DD): ")
            end_date = get_date("Enter the end date (YYYY-MM-DD): ")
            df = manager.get_transactions(start_date, end_date)
            if not df.empty and input("Do you want to see a plot? (y/n): ").lower() == "y":
                manager.plot_transactions(df)

        elif choice == "3":
            manager.generate_category_breakdown()

        elif choice == "4":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()

