from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dev-key-change-this'

def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  amount REAL NOT NULL,
                  description TEXT NOT NULL,
                  category TEXT,
                  date DATE NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn = get_db()
    
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    
    today = datetime.now()
    month_start = today.replace(day=1).strftime('%Y-%m-%d')
    month_end = today.strftime('%Y-%m-%d')
    
    month_stats = conn.execute('''
        SELECT SUM(amount) as total, COUNT(*) as count 
        FROM expenses 
        WHERE date BETWEEN ? AND ?
    ''', (month_start, month_end)).fetchone()
    
    categories = conn.execute('''
        SELECT category, SUM(amount) as total 
        FROM expenses 
        WHERE date BETWEEN ? AND ?
        GROUP BY category
    ''', (month_start, month_end)).fetchall()
    
    conn.close()
    
    monthly_total = month_stats['total'] if month_stats['total'] else 0
    monthly_count = month_stats['count'] if month_stats['count'] else 0
    
    return render_template('index.html', 
                         expenses=expenses,
                         monthly_total=monthly_total,
                         monthly_count=monthly_count,
                         categories=categories,
                         current_month=today.strftime('%B %Y'))

@app.route('/add', methods=['POST'])
def add_expense():
    amount = request.form.get('amount')
    description = request.form.get('description')
    category = request.form.get('category')
    date = request.form.get('date')
    
    if not amount or not description:
        flash('Please fill amount and description', 'error')
        return redirect('/')
    
    try:
        conn = get_db()
        conn.execute('INSERT INTO expenses (amount, description, category, date) VALUES (?, ?, ?, ?)',
                    (float(amount), description, category, date))
        conn.commit()
        conn.close()
        flash('Expense added successfully!', 'success')
    except Exception as e:
        flash('Error adding expense', 'error')
    
    return redirect('/')

@app.route('/delete/<int:expense_id>')
def delete_expense(expense_id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()
        flash('Expense deleted', 'info')
    except:
        flash('Error deleting expense', 'error')
    
    return redirect('/')

@app.route('/reports')
def reports():
    conn = get_db()
    
    all_expenses = conn.execute('SELECT * FROM expenses').fetchall()
    
    category_totals = conn.execute('''
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM expenses 
        GROUP BY category
        ORDER BY total DESC
    ''').fetchall()
    
    monthly_data = conn.execute('''
        SELECT strftime('%Y-%m', date) as month, 
               SUM(amount) as total, 
               COUNT(*) as count
        FROM expenses 
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        LIMIT 6
    ''').fetchall()
    
    total_amount = sum(expense['amount'] for expense in all_expenses)
    
    conn.close()
    
    return render_template('index.html',
                         show_reports=True,
                         category_totals=category_totals,
                         monthly_data=monthly_data,
                         total_amount=total_amount,
                         total_count=len(all_expenses))

if __name__ == '__main__':
    app.run(debug=True)