import mysql.connector
import random
import threading
import time

Conexión a la base de datos
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="43486126",
    database="preguntados",
    port='3306'
)
cursor = conn.cursor(dictionary=True)

# Borrar datos anteriores
#cursor.execute("DELETE FROM historial")
#cursor.execute("DELETE FROM jugadores")
#conn.commit()

RONDAS_POR_JUGADOR = 5
TIEMPO_LIMITE = 10
respuesta_usuario = None

def obtener_pregunta_aleatoria():
    cursor.execute("""
        SELECT p.*, c.nombre AS categoria 
        FROM preguntas p 
        JOIN categorias c ON p.categoria_id = c.id 
        ORDER BY RAND() LIMIT 1
    """)
    return cursor.fetchone()

def esperar_respuesta():
    global respuesta_usuario
    respuesta_usuario = input("\n⏳ Escribí tu respuesta (1-3): ")

def hacer_pregunta(jugador, pregunta):
    global respuesta_usuario
    respuesta_usuario = None

    opciones = [pregunta["opcion1"], pregunta["opcion2"], pregunta["opcion3"]]

    if pregunta["opcion_correcta"] not in opciones:
        opciones.append(pregunta["opcion_correcta"])
    opciones = random.sample(opciones, 3)
    random.shuffle(opciones)

    print(f"\n🎯 {jugador['nombre']} - Categoría: {pregunta['categoria']} - Puntaje: {jugador['puntaje']} - Racha: {jugador['racha']} - Vidas: {jugador['vidas']}")
    print(pregunta["pregunta"])
    for i, op in enumerate(opciones, 1):
        print(f"{i}. {op}")

    print(f"⏳ Tenés {TIEMPO_LIMITE} segundos para responder...")

    hilo_respuesta = threading.Thread(target=esperar_respuesta)
    hilo_respuesta.start()
    hilo_respuesta.join(timeout=TIEMPO_LIMITE)

    if hilo_respuesta.is_alive():
        print("\n⏰ ¡Se acabó el tiempo! Turno perdido.")
        jugador["racha"] = 0
        jugador["vidas"] -= 1
        print(f"💔 {jugador['nombre']} perdió una vida. Vidas restantes: {jugador['vidas']}")
        return

    if respuesta_usuario not in ['1', '2', '3']:
        print("❌ Respuesta inválida.")
        jugador["racha"] = 0
        jugador["vidas"] -= 1
        print(f"💔 {jugador['nombre']} perdió una vida. Vidas restantes: {jugador['vidas']}")
        return

    seleccion = opciones[int(respuesta_usuario) - 1]
    fue_correcta = (seleccion == pregunta["opcion_correcta"])

    if fue_correcta:
        print("✅ Correcto")
        jugador["puntaje"] += 1
        jugador["racha"] += 1
        if jugador["racha"] >= 3:
            print(f"🔥 ¡{jugador['nombre']} está en racha de {jugador['racha']} aciertos!")
    else:
        print(f"❌ Incorrecto. Era: {pregunta['opcion_correcta']}")
        jugador["racha"] = 0
        jugador["vidas"] -= 1
        print(f"💔 {jugador['nombre']} perdió una vida. Vidas restantes: {jugador['vidas']}")

    cursor.execute("SELECT id FROM jugadores WHERE nombre = %s", (jugador["nombre"],))
    resultado = cursor.fetchone()
    if resultado:
        jugador_id = resultado["id"]
    else:
        cursor.execute("INSERT INTO jugadores (nombre, puntaje) VALUES (%s, %s)", (jugador["nombre"], 0))
        conn.commit()
        jugador_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO historial (jugador_id, pregunta_id, fue_correcta) VALUES (%s, %s, %s)",
        (jugador_id, pregunta["id"], fue_correcta)
    )
    conn.commit()

def jugar():
    print("🎉 Bienvenidos a Preguntados 🎉\n")

    jugadores = []
    for i in range(2):
        nombre = input(f"Ingrese el nombre del Jugador {i+1}: ")
        jugadores.append({"nombre": nombre, "puntaje": 0, "racha": 0, "vidas": 3})

    for ronda in range(RONDAS_POR_JUGADOR):
        for jugador in jugadores:
            if jugador["vidas"] <= 0:
                print(f"\n❌ {jugador['nombre']} está eliminado. Sin vidas.")
                continue
            print(f"\n🔔 Ronda {ronda + 1} para {jugador['nombre']} (Vidas: {jugador['vidas']})")
            pregunta = obtener_pregunta_aleatoria()
            if pregunta:
                hacer_pregunta(jugador, pregunta)
            else:
                print("⚠️ No hay preguntas disponibles.")

    print("\n🎯 Resultado final:")
    for j in jugadores:
        print(f"{j['nombre']}: {j['puntaje']} puntos (Vidas restantes: {j['vidas']})")

    jugadores_vivos = [j for j in jugadores if j["vidas"] > 0]

    if len(jugadores_vivos) == 0:
        print("\n☠️ Todos los jugadores fueron eliminados.")
    elif jugadores[0]['puntaje'] > jugadores[1]['puntaje']:
        print(f"\n🏆 ¡Ganador: {jugadores[0]['nombre']}!")
    elif jugadores[1]['puntaje'] > jugadores[0]['puntaje']:
        print(f"\n🏆 ¡Ganador: {jugadores[1]['nombre']}!")
    else:
        print("\n🤝 ¡Empate!")

    return jugadores

if __name__ == "__main__":
    jugadores = jugar()

    for j in jugadores:
        cursor.execute("UPDATE jugadores SET puntaje = %s WHERE nombre = %s", (j["puntaje"], j["nombre"]))
    conn.commit()

    print("\n--- RESUMEN DEL JUEGO ---")

    cursor.execute("SELECT COUNT(*) AS total FROM historial")
    row = cursor.fetchone()
    print(f"Total de preguntas respondidas: {row['total']}")

    cursor.execute("SELECT COUNT(*) AS total FROM historial WHERE fue_correcta = TRUE")
    row = cursor.fetchone()
    print(f"Respuestas correctas: {row['total']}")

    cursor.execute("SELECT COUNT(*) AS total FROM historial WHERE fue_correcta = FALSE")
    row = cursor.fetchone()
    print(f"Respuestas incorrectas: {row['total']}")

    cursor.execute("SELECT nombre, puntaje FROM jugadores ORDER BY puntaje DESC")
    jugadores = cursor.fetchall()
    print("\nPuntajes de jugadores:")
    if jugadores:
        for jugador in jugadores:
            print(f"- {jugador['nombre']}: {jugador['puntaje']} puntos")
    else:
        print("No hay jugadores registrados.")
