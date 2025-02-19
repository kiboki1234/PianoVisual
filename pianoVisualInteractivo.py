import pygame
import cv2
import mediapipe as mp
import os
import time
import math
import random

# Configurar Pygame para baja latencia
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=64)
pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diccionario de archivos de audio
NOTE_FILES = {
    'C': 'Do.mp3', 'D': 'Re.mp3', 'E': 'Mi.mp3', 'F': 'Fa.mp3',
    'G': 'Sol.mp3', 'A': 'La.mp3', 'B': 'Si.mp3', 'C2': 'Do2.mp3'
}

# Cargar sonidos con manejo de errores
notes = {}
for note, filename in NOTE_FILES.items():
    note_path = os.path.join(BASE_DIR, 'AudiosPiano', filename)
    if os.path.exists(note_path):
        notes[note] = pygame.mixer.Sound(note_path)
    else:
        print(f"⚠️ Advertencia: No se encontró {note_path}")

# Mapeo de notas por dedo
HAND_MAPPINGS = {
    "Left": {'pinky': 'C', 'ring': 'D', 'middle': 'E', 'index': 'F', 'thumb': 'G'},
    "Right": {'thumb': 'A', 'index': 'B', 'middle': 'C2'}
}

# Posiciones horizontales predefinidas para cada nota
NOTE_X_POSITIONS = {
    'C': 100, 'D': 250, 'E': 400, 'F': 550, 'G': 700,
    'A': 850, 'B': 1000, 'C2': 1150
}

# Landmarks de MediaPipe para los dedos
FINGER_LANDMARKS = {'thumb': 4, 'index': 8, 'middle': 12, 'ring': 16, 'pinky': 20}

# --- Configuración de la melodía ---
melody = [
    'E', 'E', 'F', 'G', 'G', 'F', 'E', 'D', 'C', 'C', 'D', 'E', 'E', 'D', 'D',
    'E', 'E', 'F', 'G', 'G', 'F', 'E', 'D', 'C', 'C', 'D', 'E', 'D', 'C', 'C',
    'D', 'D', 'E', 'C', 'D', 'E', 'F', 'E', 'C', 'D', 'E', 'F', 'E', 'D',
    'C', 'D', 'G', 'E', 'E', 'F', 'G', 'G', 'F', 'E', 'D', 'C', 'C', 'D', 'E', 'D', 'C', 'C'
]
melody_sequence = melody * 1  # Puedes repetir la melodía si lo deseas
TOTAL_NOTES = len(melody_sequence)
current_note_index = 0

# Lista de notas en caída y control de tiempos
falling_notes = []
last_spawn_time = time.time()
SPAWN_INTERVAL = 1.0  # Intervalo entre aparición de notas

# Puntuación y combo
score = 0
combo = 0
last_hit_time = 0

# Lista para partículas
particles = []

class FallingNote:
    """Clase para manejar las notas en caída."""
    def __init__(self, note, x, y, speed=4):
        self.note = note
        self.x = x
        self.y = y
        self.speed = speed

def spawn_falling_note():
    global current_note_index, last_spawn_time
    if current_note_index < TOTAL_NOTES:
        note_key = melody_sequence[current_note_index]
        current_note_index += 1
        x = NOTE_X_POSITIONS.get(note_key, 100)
        falling_notes.append(FallingNote(note_key, x, y=0))
        last_spawn_time = time.time()

def spawn_particles(x, y, color, count=20):
    """Genera partículas en la posición (x, y) con un color dado."""
    for _ in range(count):
        # Cada partícula tendrá una velocidad y ángulo aleatorios
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        particles.append({
            'x': x,
            'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'radius': random.randint(2, 4),
            'color': color,
            'lifetime': random.uniform(0.5, 1.0),
            'birth': time.time()
        })

def update_and_draw_particles(frame):
    """Actualiza y dibuja las partículas; elimina las que expiran."""
    current_time = time.time()
    for p in particles[:]:
        # Actualiza posición
        p['x'] += p['vx']
        p['y'] += p['vy']
        # Disminuir el radio con el tiempo (efecto de desvanecimiento)
        elapsed = current_time - p['birth']
        if elapsed > p['lifetime']:
            particles.remove(p)
        else:
            # Dibujar la partícula
            alpha = max(0, 1 - elapsed / p['lifetime'])
            # Convertir alpha a escala de 0-255 para el color (no hay transparencia en cv2, pero podemos simularlo con el tamaño)
            radius = max(1, int(p['radius'] * alpha))
            cv2.circle(frame, (int(p['x']), int(p['y'])), radius, p['color'], -1)

def process_hand(hand_landmarks, hand_label, frame, w, h):
    global score, combo, last_hit_time
    mapping = HAND_MAPPINGS.get(hand_label, {})
    for finger, assigned_note in mapping.items():
        tip_idx = FINGER_LANDMARKS[finger]
        tip = hand_landmarks.landmark[tip_idx]
        tip_x, tip_y = int(tip.x * w), int(tip.y * h)
        
        cv2.circle(frame, (tip_x, tip_y), 10, (0, 255, 0), -1)
        cv2.putText(frame, assigned_note, (tip_x - 20, tip_y - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        for fn in falling_notes[:]:
            if fn.note == assigned_note:
                distancia = math.hypot(fn.x - tip_x, fn.y - tip_y)
                if distancia < 25:
                    if assigned_note in notes:
                        notes[assigned_note].play()
                    
                    # Al tocar la nota, generamos partículas en la posición de impacto
                    spawn_particles(tip_x, tip_y, (0, 255, 255))
                    
                    current_time = time.time()
                    if current_time - last_hit_time < 1.5:
                        combo += 1
                    else:
                        combo = 1
                    last_hit_time = current_time
                    score += 10 * combo
                    
                    falling_notes.remove(fn)

def main():
    global last_spawn_time
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8, min_tracking_confidence=0.8)
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    cv2.namedWindow('Piano Virtual', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Piano Virtual', cv2.WND_PROP_FULLSCREEN, 1)
    
    # --- Cuenta regresiva de inicio ---
    countdown_time = 3
    countdown_start = time.time()
    while time.time() - countdown_start < countdown_time:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        remaining = int(countdown_time - (time.time() - countdown_start)) + 1
        cv2.putText(frame, f"Comenzando en: {remaining}", (w//2 - 200, h//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)
        cv2.imshow('Piano Virtual', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            return

    # --- Bucle principal del juego ---
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        h, w = frame.shape[:2]

        if current_note_index < TOTAL_NOTES and time.time() - last_spawn_time > SPAWN_INTERVAL:
            spawn_falling_note()

        for fn in falling_notes[:]:
            fn.y += fn.speed
            cv2.circle(frame, (int(fn.x), int(fn.y)), 15, (255, 0, 0), -1)
            cv2.putText(frame, fn.note, (int(fn.x) - 20, int(fn.y) - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
            if fn.y > h:
                falling_notes.remove(fn)

        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                process_hand(hand_landmarks, handedness.classification[0].label, frame, w, h)

        # Actualizar y dibujar partículas
        update_and_draw_particles(frame)

        cv2.putText(frame, f"Puntuacion: {score}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(frame, f"Combo x{combo}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "ESC para salir", (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # --- Animación de combo ---
        if combo > 1:
            pulse = abs(math.sin(time.time() * 5))
            combo_color = (int(255 * pulse), int(255 * (1 - pulse)), 128)
            cv2.rectangle(frame, (0, 0), (w - 1, h - 1), combo_color, 10)
            if combo >= 3:
                combo_msg = f"COMBO x{combo}!"
                (msg_width, msg_height), _ = cv2.getTextSize(combo_msg, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)
                msg_x = (w - msg_width) // 2
                msg_y = (h + msg_height) // 2 - 100
                cv2.putText(frame, combo_msg, (msg_x, msg_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, combo_color, 3)

        cv2.imshow('Piano Virtual', frame)

        if current_note_index >= TOTAL_NOTES and len(falling_notes) == 0:
            break

        if cv2.waitKey(1) & 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            return

    # --- Pantalla final ---
    final_message_duration = 5
    final_start = time.time()
    while time.time() - final_start < final_message_duration:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        mensaje = f"Felicidades! Puntuacion final: {score}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 2
        thickness = 3
        (text_width, text_height), _ = cv2.getTextSize(mensaje, font, scale, thickness)
        x = (w - text_width) // 2
        y = (h + text_height) // 2
        cv2.putText(frame, mensaje, (x, y),
                    font, scale, (0, 255, 0), thickness)
        cv2.imshow('Piano Virtual', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
