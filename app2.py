import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from io import BytesIO

# Create database
def create_db():
    conn = sqlite3.connect("expenses2.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses2
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, Date TEXT, Category TEXT, Item TEXT, Quantity INTEGER, Amount REAL, Total REAL)''')
    conn.commit()
    conn.close()

# Insert expense
def insert_expense(date, category, item, quantity, amount):
    total = quantity * amount
    conn = sqlite3.connect("expenses2.db")
    c = conn.cursor()
    c.execute("INSERT INTO expenses2 (Date, Category, Item, Quantity, Amount, Total) VALUES (?, ?, ?, ?, ?, ?)", (date, category, item, quantity, amount, total))
    conn.commit()
    conn.close()

# Fetch expenses
def fetch_expenses():
    conn = sqlite3.connect("expenses2.db")
    c = conn.cursor()
    c.execute("SELECT id, Date, Category, Item, Quantity, Amount, Total FROM expenses2")
    data = c.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=["ID", "Date", "Category", "Item", "Quantity", "Amount", "Total"])

# Delete expense
def delete_expense(expense_id):
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

# Main App
def main():
    st.set_page_config(layout="wide", page_title="💰 Personal Expense Analyzer")
    st.title("💰 Personal Expense Analyzer")
    create_db()

    # Input fields
    date = st.date_input("Date")
    categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Others"]
    category = st.selectbox("Category", categories)
    item = st.text_input("Item")
    quantity = st.number_input("Quantity", min_value=1, step=1)
    amount = st.number_input("Amount (Per Item)", min_value=0.0, format="%.2f")

    if st.button("Add Expense"):
        if date and category and item and quantity and amount:
            insert_expense(str(date), category, item, quantity, amount)
            st.success("Expense Added!")
        else:
            st.warning("Please enter all details!")

    # Fetch and Display data
    expenses_df = fetch_expenses()
    if not expenses_df.empty:
        st.subheader("Expenses List")
        st.dataframe(expenses_df)
        
        # Delete functionality
        expense_id = st.number_input("Enter ID to Delete Expense", min_value=1, step=1)
        if st.button("Delete Expense"):
            delete_expense(expense_id)
            st.success("Expense Deleted!")

        # Visualization - Pie Chart
        st.subheader("Expense Analysis")
        category_totals = expenses_df.groupby("Category")["Total"].sum()
        fig, ax = plt.subplots()
        category_totals.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=["#FF9999", "#66B3FF", "#99FF99", "#FFCC99", "#FFD700", "#FF6F61"])
        ax.set_ylabel('')
        st.pyplot(fig)
        
        # Budget Alert
        budget_limit = st.number_input("Set Budget Limit", min_value=0.0, format="%.2f")
        total_expense = expenses_df["Total"].sum()
        if budget_limit > 0 and total_expense > budget_limit:
            st.error(f"Alert! You have exceeded your budget limit of {budget_limit} with total expense of {total_expense}")
        
        # Monthly Comparison Bar Chart
        st.subheader("Monthly Expense Comparison")
        expenses_df["Date"] = pd.to_datetime(expenses_df["Date"], errors='coerce')
        expenses_df.dropna(subset=["Date"], inplace=True)
        expenses_df["Month"] = expenses_df["Date"].dt.to_period("M")
        monthly_totals = expenses_df.groupby("Month")["Total"].sum()
        fig2, ax2 = plt.subplots()
        monthly_totals.plot(kind='bar', ax=ax2, color="#66B3FF")
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Total Expense")
        ax2.set_title("Monthly Expense Comparison")
        st.pyplot(fig2)
        
        # Download option
        st.subheader("Download Data")
        csv = expenses_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="expenses2.csv", mime="text/csv")

if __name__ == "__main__":
    main()
