import mysql.connector

with open("init_db.sql") as f:
    sql = f.read()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

cursor = conn.cursor()

for statement in sql.split(";"):
    if statement.strip():
        print(f"Ejecutando: {statement.strip()}")
        cursor.execute(statement)
        conn.commit()
        print("ejecutado correctamente")

cursor.close()
conn.close()

