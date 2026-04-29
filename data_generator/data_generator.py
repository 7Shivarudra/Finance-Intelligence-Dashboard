import pandas as pd
import random
import os
from datetime import datetime, timedelta

# -------------------------------
# 🧠 CATEGORIES
# -------------------------------
categories = {
    "Food": ["Swiggy", "Zomato", "Cafe"],
    "Groceries": ["BigBasket", "Reliance Mart"],
    "Transport": ["Uber", "Fuel"],
    "Shopping": ["Amazon", "Mall"],
    "Entertainment": ["Netflix", "Movies"],
    "Utilities": ["Electricity", "Internet", "Rent"],
    "Healthcare": ["Pharmacy", "Clinic"],
    "Travel": ["Flight", "Hotel"],
    "Fitness": ["Gym"],
    "Subscriptions": ["Spotify", "Netflix"]
}

payment_modes = ["UPI", "Card", "NetBanking"]

# -------------------------------
# 🏦 LOANS
# -------------------------------
loan_types = {
    "Home Loan": {"interest": 0.08, "tenure": 240},
    "Education Loan": {"interest": 0.06, "tenure": 120},
    "Car Loan": {"interest": 0.09, "tenure": 60},
    "Personal Loan": {"interest": 0.12, "tenure": 36}
}

# -------------------------------
# 📈 INVESTMENTS
# -------------------------------
investment_types = ["Stocks", "Mutual Fund", "Crypto"]

# -------------------------------
# ⏰ TIME
# -------------------------------
def random_time(category):
    if category in ["Food", "Entertainment"]:
        hour = random.randint(18, 23)
    else:
        hour = random.randint(9, 20)
    return f"{hour:02d}:{random.randint(0,59):02d}:00"

# -------------------------------
# FILE NAMING
# -------------------------------
def get_next_filename(profile):
    i = 1
    while True:
        name = f"{profile}_dataset_{i}.xlsx"
        if not os.path.exists(name):
            return name
        i += 1

# -------------------------------
# EMI
# -------------------------------
def calculate_emi(p, r, n):
    r = r / 12
    return int(p * r * (1 + r)**n / ((1 + r)**n - 1))

# -------------------------------
# GENERATOR
# -------------------------------
def generate_data(profile, n, start_balance):

    data = []
    balance = start_balance
    loans = []
    investments = []

    start_date = datetime(2024, 1, 1)

    for i in range(n):

        date = start_date + timedelta(days=i // 3)
        weekday = date.weekday()

        debit = 0
        credit = 0
        loan_taken = 0
        emi_paid = 0
        loan_type = ""
        investment_amt = 0
        returns_amt = 0

        # -----------------------
        # SALARY
        # -----------------------
        if date.day == 1:
            credit = random.randint(30000, 80000)
            category = "Salary"
            transaction = "Monthly Salary"

        # -----------------------
        # SMART LOAN DECISION
        # -----------------------
        elif balance < 5000 and len(loans) < 2 and random.random() < 0.3:

            loan_type = random.choice(list(loan_types.keys()))
            info = loan_types[loan_type]

            principal = random.randint(30000, 200000)
            emi = calculate_emi(principal, info["interest"], info["tenure"])

            loans.append({
                "type": loan_type,
                "remaining": principal,
                "emi": emi,
                "interest": info["interest"],
                "months": info["tenure"]
            })

            credit = principal
            loan_taken = principal
            category = "Loan Credit"
            transaction = loan_type

        # -----------------------
        # EMI PAYMENT
        # -----------------------
        elif loans and random.random() < 0.2:
            loan = random.choice(loans)

            emi_paid = loan["emi"]
            interest = loan["remaining"] * (loan["interest"]/12)
            principal_paid = emi_paid - interest

            loan["remaining"] -= principal_paid
            loan["months"] -= 1

            debit = emi_paid
            category = "Loan EMI"
            transaction = loan["type"]

            if loan["remaining"] <= 0:
                loans.remove(loan)

        # -----------------------
        # INVESTMENT (SMART)
        # -----------------------
        elif balance > 20000 and random.random() < 0.1:

            investment_amt = random.randint(2000, 15000)
            debit = investment_amt

            future_date = date + timedelta(days=random.randint(10, 60))

            investments.append({
                "amount": investment_amt,
                "date": future_date
            })

            category = "Investment"
            transaction = random.choice(investment_types)

        # -----------------------
        # RETURNS (profit/loss)
        # -----------------------
        elif investments and random.random() < 0.15:
            inv = random.choice(investments)

            if date >= inv["date"]:
                percent = random.uniform(-0.2, 0.3)
                returns_amt = int(inv["amount"] * percent)

                credit = inv["amount"] + returns_amt
                if credit < 0:
                    credit = 0

                investments.remove(inv)

                category = "Investment Return"
                transaction = "Return"

        # -----------------------
        # EXPENSES
        # -----------------------
        else:
            category = random.choice(list(categories.keys()))
            transaction = random.choice(categories[category])

            if weekday >= 5:
                debit = random.randint(500, 8000)
            else:
                debit = random.randint(100, 4000)

            if random.random() < 0.05:
                debit *= random.randint(2, 5)

        # -----------------------
        # UPDATE BALANCE
        # -----------------------
        balance = balance + credit - debit

        total_loan = sum(l["remaining"] for l in loans)

        data.append([
            f"TXN{100000+i}",
            date.date(),
            random_time(category),
            transaction,
            category,
            debit,
            credit,
            investment_amt,
            returns_amt,
            loan_type,
            loan_taken,
            emi_paid,
            total_loan,
            balance,
            random.choice(payment_modes)
        ])

    df = pd.DataFrame(data, columns=[
        "Transaction_ID",
        "Date",
        "Time",
        "Transaction",
        "Category",
        "Debit",
        "Credit",
        "Investment",
        "Returns",
        "Loan_Type",
        "Loan_Taken",
        "EMI_Paid",
        "Outstanding_Loan",
        "Balance",
        "Payment_Mode"
    ])

    return df.sort_values(by=["Date", "Time"]).reset_index(drop=True)


# -------------------------------
# INPUT
# -------------------------------
choice = input("Profile (profit/loss/balanced): ")
size = int(input("Records: "))
balance = int(input("Starting balance: "))

df = generate_data(choice, size, balance)

file_name = get_next_filename(choice)
df.to_excel(file_name, index=False)

print(f"\n✅ Dataset generated: {file_name}")