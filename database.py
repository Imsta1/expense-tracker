import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_expense(amount, description, category, date):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO expenses (amount, description, category, date)
        VALUES (?, ?, ?, ?)
    ''', (amount, description, category, date))
    conn.commit()
    conn.close()

def get_all_expenses():
    conn = get_db_connection()
    expenses = conn.execute('''
        SELECT * FROM expenses 
        ORDER BY date DESC
    ''').fetchall()
    conn.close()
    return expenses

def delete_expense(expense_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()

def get_monthly_summary():
    conn = get_db_connection()
    
    current_month = datetime.now().strftime('%Y-%m')
    
    result = conn.execute('''
        SELECT SUM(amount) as total, COUNT(*) as count 
        FROM expenses 
        WHERE strftime('%Y-%m', date) = ?
    ''', (current_month,)).fetchone()
    
    conn.close()
    
    return {
        'total': result['total'] or 0,
        'count': result['count'] or 0
    }

def get_category_totals():
    conn = get_db_connection()
    
    current_month = datetime.now().strftime('%Y-%m')
    
    results = conn.execute('''
        SELECT category, SUM(amount) as total 
        FROM expenses 
        WHERE strftime('%Y-%m', date) = ?
        GROUP BY category
    ''', (current_month,)).fetchall()
    
    conn.close()
    
    categories = {}
    for row in results:
        categories[row['category']] = row['total']
    
    return categories