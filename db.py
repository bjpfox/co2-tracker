import psycopg2
from psycopg2.extras import RealDictCursor

def sql_select_all(query, params=None):
    conn = psycopg2.connect("dbname=co2_tracker")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def sql_select_one(query, params=None):
    conn = psycopg2.connect("dbname=co2_tracker")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

def sql_write(query, params=None):
    conn = psycopg2.connect("dbname=co2_tracker")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params)
    conn.commit() 
    cur.close()
    conn.close()

def is_sql_query_valid(query, params=None):
    conn = psycopg2.connect("dbname=co2_tracker")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(query, params)
    status_message = cur.statusmessage
    cur.close()
    conn.close()
    return status_message
    