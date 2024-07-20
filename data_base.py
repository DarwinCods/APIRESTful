import sqlite3

conexion = sqlite3.connect('obras.db')

cursor = conexion.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS libros(
id INTEGER PRIMARY KEY AUTOINCREMENT,
titulo VARCHAR(255),
descripcion TEXT,
autor VARCHAR(100),
precio INT(255)
)
"""
               )

conexion.commit()


cursor.execute("""
CREATE TABLE IF NOT EXISTS peliculas(
id INTEGER PRIMARY KEY AUTOINCREMENT,
titulo VARCHAR(255),
descripcion TEXT,
director VARCHAR(100),
precio INT(255)
)
"""
               )

conexion.commit()

#cursor.executemany("INSERT INTO libros (titulo, descripcion, autor ,precio) values(?, ?, ? ,?)", (listaProductos))

#cursor.execute("delete from libros")
#conexion.commit()

# Recuperar los datos para verificar la inserción (opcional)
cursor.execute("select * from peliculas")
insertar = cursor.fetchall()

for i in insertar:
    print(i)


