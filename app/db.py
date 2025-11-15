import sqlite3

def get_local_guidance(symptom):
    conn = sqlite3.connect("health.db")
    cursor = conn.cursor()
    cursor.execute("SELECT advice FROM health WHERE symptom=?", (symptom,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None