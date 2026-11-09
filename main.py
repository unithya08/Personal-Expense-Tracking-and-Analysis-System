import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import base64
from io import BytesIO
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
from config import get_db_connection
from datetime import date

app = Flask(__name__)
app.secret_key = "expense-tracker-dev-key"


# Home page: display and filter expenses
@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Read filters selected on the website
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    category_id = request.args.get("category_id", "")

    # Build the SQL query
    query = """
        SELECT e.expense_id, e.expense_date, e.amount,
               e.description, e.payment_method,
               e.category_id, c.category_name
        FROM expenses e
        JOIN categories c ON e.category_id = c.category_id
        WHERE 1=1
    """
    params = []

    if start_date:
        query += " AND e.expense_date >= %s"
        params.append(start_date)

    if end_date:
        query += " AND e.expense_date <= %s"
        params.append(end_date)

    if category_id:
        query += " AND e.category_id = %s"
        params.append(category_id)

    query += " ORDER BY e.expense_date DESC, e.expense_id DESC"

    cursor.execute(query, tuple(params))
    expenses = cursor.fetchall()

    # Get categories for the dropdown
    cursor.execute("""
        SELECT category_id, category_name
        FROM categories
        ORDER BY category_name
    """)
    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    # Calculate total for the currently displayed expenses
    total = sum(float(e["amount"]) for e in expenses)

    return render_template(
        "index.html",
        expenses=expenses,
        categories=categories,
        total=total,
        start_date=start_date,
        end_date=end_date,
        selected_category=category_id
    )

# Add an expense
@app.route("/add", methods=["POST"])
def add_expense():
    try:

        expense_date = date.fromisoformat(request.form["expense_date"])
        amount = float(request.form["amount"])
        category_id = int(request.form["category_id"])

        if amount <= 0:
            raise ValueError("Amount must be positive.")

        if expense_date > date.today():
            raise ValueError("Expense date cannot be in the future.")

        # Confirm that the selected category exists
        check_conn = get_db_connection()
        check_cursor = check_conn.cursor()

        check_cursor.execute(
            "SELECT category_id FROM categories WHERE category_id = %s",
            (category_id,)
        )
        category_exists = check_cursor.fetchone() is not None

        check_cursor.close()
        check_conn.close()

        if not category_exists:
            raise ValueError("Please select a valid category.")

        description = request.form.get("description", "").strip()
        payment_method = request.form.get("payment_method", "Cash")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expenses
            (expense_date, category_id, amount, description, payment_method)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            expense_date, category_id, amount,
            description, payment_method
        ))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Expense added successfully!")

    except (ValueError, TypeError, KeyError):
        flash("Enter a valid date, category and positive amount.")

    return redirect(url_for("index"))


# Edit an existing expense
@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        try:

            expense_date = date.fromisoformat(request.form["expense_date"])
            amount = float(request.form["amount"])
            category_id = int(request.form["category_id"])

            if amount <= 0:
                raise ValueError("Amount must be positive.")

            if expense_date > date.today():
                raise ValueError("Expense date cannot be in the future.")

            # Check that the selected category exists
            cursor.execute(
                "SELECT category_id FROM categories WHERE category_id = %s",
                (category_id,)
            )
            if cursor.fetchone() is None:
                raise ValueError("Please select a valid category.")

            description = request.form.get("description", "").strip()
            payment_method = request.form.get(
                "payment_method", "Cash"
            )

            cursor.execute(
                """UPDATE expenses
                   SET expense_date=%s, amount=%s, category_id=%s,
                       description=%s, payment_method=%s
                   WHERE expense_id=%s""",
                (
                    expense_date, amount, category_id,
                    description, payment_method, expense_id
                )
            )

            conn.commit()
            flash("Expense updated successfully!")
            cursor.close()
            conn.close()
            return redirect(url_for("index"))

        except (ValueError, TypeError, KeyError):
            flash("Enter a valid date, category and positive amount.")

    cursor.execute(
        "SELECT * FROM expenses WHERE expense_id=%s",
        (expense_id,)
    )
    expense = cursor.fetchone()

    cursor.execute(
        "SELECT category_id, category_name FROM categories"
    )
    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    if expense is None:
        flash("Expense not found.")
        return redirect(url_for("index"))

    return render_template(
        "edit.html", expense=expense, categories=categories
    )


# Delete an expense
@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE expense_id=%s",
        (expense_id,)
    )

    conn.commit()
    deleted = cursor.rowcount

    cursor.close()
    conn.close()

    flash(
        "Expense deleted successfully!"
        if deleted else "Expense not found."
    )

    return redirect(url_for("index"))


# Analytics page
@app.route("/analytics")
def analytics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT e.expense_date, e.amount, c.category_name
        FROM expenses e
        JOIN categories c ON e.category_id = c.category_id
        ORDER BY e.expense_date
    """)

    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    # Handle the case where no expenses exist
    if not expenses:
        return render_template(
            "analytics.html",
            has_data=False
        )

    # Convert database records into a Pandas DataFrame
    df = pd.DataFrame(expenses)

    # Ensure dates and amounts have the correct data types
    df["expense_date"] = pd.to_datetime(df["expense_date"])
    df["amount"] = pd.to_numeric(df["amount"])

    # Total and average spending
    total_spending = float(df["amount"].sum())
    average_expense = float(np.mean(df["amount"]))

    # Category-wise spending
    category_totals = (
        df.groupby("category_name")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    category_data = [
        {
            "category": str(category),
            "amount": float(amount),
            "percentage": float(amount / total_spending * 100)
        }
        for category, amount in category_totals.items()
    ]

    highest_category = category_data[0]["category"]
    highest_amount = category_data[0]["amount"]

    # Month-wise spending
    df["month"] = df["expense_date"].dt.to_period("M").astype(str)

    monthly_totals = (
        df.groupby("month")["amount"]
        .sum()
        .sort_index()
    )

    monthly_data = [
        {
            "month": str(month),
            "amount": float(amount)
        }
        for month, amount in monthly_totals.items()
    ]

    # Create the category-wise pie chart
    pie_fig, pie_ax = plt.subplots(figsize=(7, 5))

    pie_ax.pie(
        category_totals.values,
        labels=category_totals.index,
        autopct="%1.1f%%",
        startangle=90
    )
    pie_ax.set_title("Category-wise Spending")
    pie_fig.tight_layout()

    pie_buffer = BytesIO()
    pie_fig.savefig(pie_buffer, format="png", bbox_inches="tight")
    pie_buffer.seek(0)
    category_chart = base64.b64encode(
        pie_buffer.getvalue()
    ).decode("utf-8")

    plt.close(pie_fig)
    pie_buffer.close()

    # Create the month-wise bar chart
    bar_fig, bar_ax = plt.subplots(figsize=(8, 5))

    bar_ax.bar(monthly_totals.index, monthly_totals.values)
    bar_ax.set_title("Monthly Spending")
    bar_ax.set_xlabel("Month")
    bar_ax.set_ylabel("Amount (₹)")
    bar_ax.tick_params(axis="x", rotation=45)
    bar_fig.tight_layout()

    bar_buffer = BytesIO()
    bar_fig.savefig(bar_buffer, format="png", bbox_inches="tight")
    bar_buffer.seek(0)
    monthly_chart = base64.b64encode(
        bar_buffer.getvalue()
    ).decode("utf-8")

    plt.close(bar_fig)
    bar_buffer.close()


    return render_template(
        "analytics.html",
        has_data=True,
        total_spending=total_spending,
        average_expense=average_expense,
        expense_count=len(df),
        highest_category=highest_category,
        highest_amount=highest_amount,
        category_data=category_data,
        monthly_data=monthly_data,
        category_chart=category_chart,
        monthly_chart=monthly_chart
    )

if __name__ == "__main__":
    app.run(debug=True)
