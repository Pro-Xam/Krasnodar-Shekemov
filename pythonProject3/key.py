import sqlite3


con = sqlite3.connect("mydata (2).SQLite", check_same_thread=False)
cur = con.cursor()

cur.execute("INSERT INTO mytable (name,text,user) VALUES ('фрфрфрр','ладно','6у324698')").fetchall()

result = cur.execute("""SELECT text FROM mytable""").fetchall()

for elem in result:
    print(list(elem))

con.commit()
con.close()

# "INSERT INTO articles ('Google', 'Google is a search', 100, 'Admin')"
