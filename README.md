# Personal Expense Tracking and Analysis System

## 1. Project Overview

The Personal Expense Tracking and Analysis System is a web application that helps users record, manage, and analyze their daily expenses. It uses Python, Flask, MySQL, Pandas, NumPy, and Matplotlib to provide expense management and visual spending analysis.

## 2. Features

- Add new expenses with date, amount, category, description, and payment method.
- View all recorded expenses.
- Edit existing expenses.
- Delete expenses.
- Filter expenses by date range and category.
- Calculate total spending and average expense.
- Identify the highest-spending category.
- Analyze category-wise spending and monthly spending.
- Display a pie chart for category-wise spending.
- Display a bar chart for monthly spending.
- Validate positive expense amounts and reject future dates.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Web application and backend routes |
| HTML and CSS | Website structure and design |
| MySQL | Store expense and category records |
| Pandas | Organize and analyze expense data |
| NumPy | Calculate numerical statistics |
| Matplotlib | Generate charts |
| mysql-connector-python | Connect Python to MySQL |

## 4. Project Structure

```text
ExpenseTracker/
├── main.py
├── config.py
├── test_db.py
├── README.md
└── templates/
    ├── index.html
    ├── edit.html
    └── analytics.html
```

## 5. Database Setup

Create a MySQL database named `expense_tracker`.

The application uses two tables:

- `categories`: stores expense categories.
- `expenses`: stores expense dates, amounts, category IDs, descriptions, and payment methods.

Create the tables and insert the default categories using the SQL setup instructions provided with the project.

## 6. Installation

Install Python and MySQL first.

Open a terminal in the project folder and install the required libraries:

```bash
python -m pip install flask mysql-connector-python pandas numpy matplotlib
```

Configure the MySQL connection settings in `config.py` using your local database credentials.

Never upload real database passwords to a public repository.

## 7. Run the Application

Start the Flask application:

```bash
python main.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

Open the analytics dashboard at:

```text
http://127.0.0.1:5000/analytics
```

## 8. Data Analysis

Pandas groups expenses by category and month. NumPy calculates the average expense. Matplotlib generates a pie chart showing category-wise spending and a bar chart comparing monthly expenses.

## 9. Testing

Test the application by adding, editing, and deleting expenses. Verify date and category filters, totals, positive amount validation, and the analytics dashboard.

## 10. Future Enhancements

- Monthly budgets and spending alerts.
- Export reports to CSV or PDF.
- User authentication and individual accounts.
- Improved dashboard and mobile-friendly design.

## 11. Conclusion

This project demonstrates how Python, Flask, MySQL, and data analysis libraries can be combined to build a practical expense management and analysis application.
