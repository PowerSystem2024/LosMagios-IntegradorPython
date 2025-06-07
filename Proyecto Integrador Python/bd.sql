import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="43486126",
    port='3306'
)
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS preguntados CHARACTER SET utf8mb4")
cursor.execute("USE preguntados")

# Limpiar tablas si existen
cursor.execute("DROP TABLE IF EXISTS historial")
cursor.execute("DROP TABLE IF EXISTS preguntas")
cursor.execute("DROP TABLE IF EXISTS categorias")
cursor.execute("DROP TABLE IF EXISTS jugadores")

# Crear tablas
cursor.execute("""
CREATE TABLE jugadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    puntaje INT DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
)
""")

cursor.execute("""
CREATE TABLE preguntas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    categoria_id INT,
    pregunta TEXT,
    opcion1 VARCHAR(255),
    opcion2 VARCHAR(255),
    opcion3 VARCHAR(255),
    opcion_correcta VARCHAR(255),
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
)
""")

cursor.execute("""
CREATE TABLE historial (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jugador_id INT,
    pregunta_id INT,
    fue_correcta BOOLEAN,
    FOREIGN KEY (jugador_id) REFERENCES jugadores(id),
    FOREIGN KEY (pregunta_id) REFERENCES preguntas(id)
)
""")

# Insertar categorías
cursor.executemany("INSERT INTO categorias (nombre) VALUES (%s)", [
    ('Ciencia',), ('Historia',), ('Geografía',), ('Arte',), ('Deportes',)
])

# Insertar preguntas
cursor.executemany("""
    INSERT INTO preguntas (categoria_id, pregunta, opcion1, opcion2, opcion3, opcion_correcta)
    VALUES (%s, %s, %s, %s, %s, %s)
""", [
    (1, '¿Cuál es el planeta más grande del sistema solar?', 'Tierra', 'Júpiter', 'Marte', 'Júpiter'),
    (1, '¿Qué gas respiramos principalmente?', 'Oxígeno', 'Nitrógeno', 'Dióxido de carbono', 'Nitrógeno'),
    (1, '¿Cuántos elementos hay en la tabla periódica?', '118', '120', '116', '118'),

    (2, '¿En qué año comenzó la Segunda Guerra Mundial?', '1935', '1939', '1941', '1939'),
    (2, '¿Quién fue el primer presidente de EE.UU.?', 'Jefferson', 'Washington', 'Lincoln', 'Washington'),
    (2, '¿Qué civilización construyó las pirámides?', 'Aztecas', 'Egipcios', 'Mayas', 'Egipcios'),

    (3, '¿Cuál es la capital de Canadá?', 'Toronto', 'Ottawa', 'Vancouver', 'Ottawa'),
    (3, '¿Dónde está el Monte Everest?', 'India', 'Tíbet', 'Nepal', 'Nepal'),
    (3, '¿Cuál es el río más largo del mundo?', 'Amazonas', 'Nilo', 'Yangtsé', 'Amazonas'),

    (4, '¿Quién pintó La última cena?', 'Da Vinci', 'Van Gogh', 'Picasso', 'Da Vinci'),
    (4, '¿Cuál es el estilo de Picasso?', 'Cubismo', 'Barroco', 'Renacimiento', 'Cubismo'),
    (4, '¿Qué instrumento tocaba Beethoven?', 'Violín', 'Piano', 'Flauta', 'Piano'),

    (5, '¿Cuántos jugadores tiene un equipo de fútbol?', '9', '10', '11', '11'),
    (5, '¿Dónde se originó el tenis?', 'Francia', 'Inglaterra', 'Estados Unidos', 'Francia'),
    (5, '¿En qué deporte se usa una pala?', 'Tenis', 'Padel', 'Golf', 'Padel')
])

conn.commit()
cursor.close()
conn.close()
print("Los quiero chicos")
