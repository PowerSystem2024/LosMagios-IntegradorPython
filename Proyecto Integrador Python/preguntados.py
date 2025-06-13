import mysql.connector
import random

# Conexión a la base de datos
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="43486126",
    database="preguntados",
    port='3306'
)
cursor = conn.cursor(dictionary=True)

RONDAS_POR_JUGADOR = 5

def obtener_pregunta_aleatoria():
    cursor.execute("""
        SELECT p.*, c.nombre AS categoria 
        FROM preguntas p 
        JOIN categorias c ON p.categoria_id = c.id 
        ORDER BY RAND() LIMIT 1
    """)
    return cursor.fetchone()

def hacer_pregunta(jugador, pregunta):
    opciones = [pregunta["opcion1"], pregunta["opcion2"], pregunta["opcion3"]]
    random.shuffle(opciones)

    print(f"\n🎯 {jugador['nombre']} - Categoría: {pregunta['categoria']} - Puntaje: {jugador['puntaje']} - Racha: {jugador['racha']}")
    print(pregunta["pregunta"])
    for i, op in enumerate(opciones, 1):
        print(f"{i}. {op}")

    respuesta = input("Respuesta (1-3): ")
    if respuesta not in ['1', '2', '3']:
        print("❌ Respuesta inválida.")
        return

    seleccion = opciones[int(respuesta)-1]
    if seleccion == pregunta["opcion_correcta"]:
        print("✅ Correcto")
        jugador["puntaje"] += 1
        jugador["racha"] += 1
        if jugador["racha"] >= 3:
            print(f"🔥 ¡{jugador['nombre']} está en racha de {jugador['racha']} aciertos!")
    else:
        print(f"❌ Incorrecto. Era: {pregunta['opcion_correcta']}")
        jugador["racha"] = 0  # Se reinicia la racha

def jugar():
    print("🎉 Bienvenidos a Preguntados 🎉\n")

    jugadores = []
    for i in range(2):
        nombre = input(f"Ingrese el nombre del Jugador {i+1}: ")
        jugadores.append({
            "nombre": nombre,
            "puntaje": 0,
            "racha": 0
        })

    for ronda in range(RONDAS_POR_JUGADOR):
        for jugador in jugadores:
            print(f"\n🔔 Ronda {ronda + 1} para {jugador['nombre']}")
            pregunta = obtener_pregunta_aleatoria()
            hacer_pregunta(jugador, pregunta)

    print("\n🎯 Resultado final:")
    for j in jugadores:
        print(f"{j['nombre']}: {j['puntaje']} puntos")

    if jugadores[0]['puntaje'] > jugadores[1]['puntaje']:
        print(f"\n🏆 ¡Ganador: {jugadores[0]['nombre']}!")
    elif jugadores[1]['puntaje'] > jugadores[0]['puntaje']:
        print(f"\n🏆 ¡Ganador: {jugadores[1]['nombre']}!")
    else:
        print("\n🤝 ¡Empate!")

if _name_ == "_main_":
    jugar()
