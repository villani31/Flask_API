import sqlite3

connection = sqlite3.connect("banco.db")
cursor = connection.cursor()

cria_tabela = "CREATE TABLE IF NOT EXISTS hoteis (hoteis_id text PRIMARY KEY,\
     nome TEXT,estrelas real, diaria real, estado text)"

cria_hote = 'INSERT INTO hoteis VALUES ("alfha", "Alfha Hotel", 4.3, 345.30,\
    "Rio de Janeiro")'

cursor.execute(cria_tabela)

connection.commit()
connection.close()