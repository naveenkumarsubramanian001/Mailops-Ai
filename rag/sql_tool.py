import sqlite3

DB_PATH = "db/db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_employee_data(employee_email):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.name, e.department, e.role, e.joined_date,
               l.sick_used, l.sick_total, 
               l.casual_used, l.casual_total
        FROM employees e
        LEFT JOIN leave_balance l ON e.employee_id = l.employee_id
        WHERE e.email = ?
    """, (employee_email,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def execute_sql_query(query, params=()):
    """
    Executes a read-only query safely.
    """
    if "DROP" in query.upper() or "DELETE" in query.upper() or "UPDATE" in query.upper() or "INSERT" in query.upper():
        return {"error": "Only SELECT queries are allowed."}
        
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        conn.close()
        return {"error": str(e)}
