import mysql.connector
import random
import threading
import time

# Conexión a la base de datos
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="43486126",
    database="preguntados",
    port='3306'
)
cursor = conn.cursor(dictionary=True)

TIEMPO_LIMITE = 10
respuesta_usuario = None
tiempo_terminado = False

def obtener_pregunta_aleatoria(categoria_nombre):
    cursor.execute("""
        SELECT p.*, c.nombre AS categoria 
        FROM preguntas p 
        JOIN categorias c ON p.categoria_id = c.id 
        WHERE c.nombre = %s
        ORDER BY RAND() LIMIT 1
    """, (categoria_nombre,))
    return cursor.fetchone()

def esperar_respuesta():
    global respuesta_usuario
    respuesta_usuario = input("\n⏳ Tenés 10 segundos. Escribí tu respuesta (1-3): ")

def cuenta_regresiva():
    global tiempo_terminado
    for i in range(TIEMPO_LIMITE, 0, -1):
        print(f"⏰ Tiempo restante: {i} segundos", end='\r')
        time.sleep(1)
    tiempo_terminado = True

def hacer_pregunta(jugador, pregunta):
    global respuesta_usuario, tiempo_terminado
    respuesta_usuario = None
    tiempo_terminado = False

    opciones_posibles = [pregunta["opcion1"], pregunta["opcion2"], pregunta["opcion3"], pregunta["opcion_correcta"]]

    if pregunta["opcion_correcta"] not in opciones_posibles:
        opciones_posibles.append(pregunta["opcion_correcta"])

    incorrectas = [op for op in opciones_posibles if op != pregunta["opcion_correcta"]]
    opciones = random.sample(incorrectas, 2) + [pregunta["opcion_correcta"]]
    random.shuffle(opciones)

    print(f"\n🎯 {jugador['nombre']} - Categoría: {pregunta['categoria']} - Puntaje: {jugador['puntaje']} - Racha: {jugador['racha']}")
    print(pregunta["pregunta"])
    for i, op in enumerate(opciones, 1):
        print(f"{i}. {op}")

    hilo_respuesta = threading.Thread(target=esperar_respuesta)
    hilo_tiempo = threading.Thread(target=cuenta_regresiva)

    hilo_respuesta.start()
    hilo_tiempo.start()

    hilo_respuesta.join(timeout=TIEMPO_LIMITE)

    if respuesta_usuario is None:
        print("\n⏰ ¡Se acabó el tiempo! Turno perdido.")
        jugador["racha"] = 0
        return

    if respuesta_usuario not in ['1', '2', '3']:
        print("❌ Respuesta inválida.")
        jugador["racha"] = 0
        return

    seleccion = opciones[int(respuesta_usuario) - 1]
    if seleccion == pregunta["opcion_correcta"]:
        print("✅ Correcto")
        jugador["puntaje"] += 1
        jugador["racha"] += 1
        if jugador["racha"] >= 3:
            print(f"🔥 ¡{jugador['nombre']} está en racha de {jugador['racha']} aciertos!")
    else:
        print(f"❌ Incorrecto. Era: {pregunta['opcion_correcta']}")
        jugador["racha"] = 0

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

    categorias = ["Ciencia", "Historia", "Geografía", "Arte", "Deportes"]

    for categoria in categorias:
        print(f"\n🔍 Cambiamos de categoría: {categoria} 🧠")
        for ronda in range(2):
            for jugador in jugadores:
                print(f"\n🔔 Ronda de {categoria} para {jugador['nombre']}")
                pregunta = obtener_pregunta_aleatoria(categoria)
                if pregunta:
                    hacer_pregunta(jugador, pregunta)
                else:
                    print(f"⚠️ No hay preguntas disponibles para la categoría: {categoria}")
                    continue

    print("\n🎯 Resultado final:")
    for j in jugadores:
        print(f"{j['nombre']}: {j['puntaje']} puntos")

    if jugadores[0]['puntaje'] > jugadores[1]['puntaje']:
        print(f"\n🏆 ¡Ganador: {jugadores[0]['nombre']}!")
    elif jugadores[1]['puntaje'] > jugadores[0]['puntaje']:
        print(f"\n🏆 ¡Ganador: {jugadores[1]['nombre']}!")
    else:
        print("\n🤝 ¡Empate!")

if __name__ == "__main__":
    jugar()