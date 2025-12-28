import sqlite3, os
db = os.path.abspath("avito_assist.db")
con = sqlite3.connect(db)
rows = con.execute("select name from sqlite_master where type='table' order by name").fetchall()
print(db)
print(rows)
