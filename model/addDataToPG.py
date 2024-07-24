from settings import uriPG
import psycopg2 as psycopg2
from psycopg2 import sql

conn = psycopg2.connect(uriPG)
cur = conn.cursor()


createQuery = sql.SQL("""
            CREATE TABLE IF NOT EXISTS dailydata (
                date DATE PRIMARY KEY,
                accuracy REAL NOT NULL,
                features TEXT NOT NULL
            )
        """)

insertQuery = sql.SQL("""
        INSERT INTO dailydata (date, accuracy, features)
        VALUES (%s, %s, %s)
    """)

getAllQuery = sql.SQL("SELECT * FROM {table}").format(
        table=sql.Identifier("dailydata")
    )

def getAll():
    conn = psycopg2.connect(uriPG)
    cur = conn.cursor()
  
    # Execute the query
    cur.execute(getAllQuery)
    
    # Fetch all rows
    rows = cur.fetchall()
    
    # Get column names
    col_names = [desc[0] for desc in cur.description]
    
    # Print column names
    print("| " + " | ".join(col_names) + " |")
    print("|" + "-|"*len(col_names))
    
    # Print each row
    for row in rows:
        print("| " + " | ".join(str(value) for value in row) + " |")
    
    print(f"\nTotal rows: {len(rows)}")

    cur.close()
    conn.close()



def checkTableExistence(tableName):
    
    # SQL query to check if table exists
    check_table_query = sql.SQL("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
    """)
    
    # Execute the query
    cur.execute(check_table_query, (tableName,))
    
    # Fetch the result
    tableExists = cur.fetchone()[0]
    
    return tableExists
    

def addDataToPG(date, accuracy, features):


    if not checkTableExistence("dailydata"):

        cur.execute(createQuery)
        
        conn.commit()
        
        print("Table created successfully")

    
    cur.execute(insertQuery, (date, accuracy, features))
    
    # Commit the transaction
    conn.commit()
    
    print("Data inserted successfully")

    






    
    if cur:
        cur.close()
    if conn:
        conn.close()
