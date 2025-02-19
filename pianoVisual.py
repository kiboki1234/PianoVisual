import pygame
import cv2
import mediapipe as mp
import os

# Configurar Pygame para baja latencia
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=64)
pygame.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diccionario de archivos de audio
NOTE_FILES = {
    'C': 'Do.mp3',
    'D': 'Re.mp3',
    'E': 'Mi.mp3',
    'F': 'Fa.mp3',
    'G': 'Sol.mp3',
    'A': 'La.mp3',
    'B': 'Si.mp3',
    'C2': 'Do2.mp3'
}

# Cargar sonidos
notes = {}
for note, filename in NOTE_FILES.items():
    note_path = os.path.join(BASE_DIR, 'AudiosPiano', filename)
    try:
        notes[note] = pygame.mixer.Sound(note_path)
    except Exception as e:
        print(f"Error al cargar {note_path}: {e}")

# Estados para detección de transición
note_states = {note: False for note in notes.keys()}

# Configuración de dedos y landmarks
FINGER_LANDMARKS = {
    'thumb': (4, 2),
    'index': (8, 5),
    'middle': (12, 9),
    'ring': (16, 13),
    'pinky': (20, 17)
}

# Mapeo de notas por mano
LEFT_HAND_MAPPING = {
    'pinky': 'C',
    'ring': 'D',
    'middle': 'E',
    'index': 'F',
    'thumb': 'G'
}

RIGHT_HAND_MAPPING = {
    'thumb': 'A',
    'index': 'B',
    'middle': 'C2'
}

THRESHOLD_OFFSET = 15  # Valor más bajo para mayor sensibilidad

def process_finger_note(frame, finger, note, hand_landmarks, w, h):
    """Detecta y reproduce notas en el movimiento descendente del dedo"""
    tip_idx, base_idx = FINGER_LANDMARKS[finger]
    tip = hand_landmarks.landmark[tip_idx]
    base = hand_landmarks.landmark[base_idx]
    
    # Convertir coordenadas normalizadas a píxeles
    tip_x, tip_y = int(tip.x * w), int(tip.y * h)
    base_y = int(base.y * h)

    # Calcular umbral de activación
    threshold = base_y - THRESHOLD_OFFSET
    current_active = tip_y > threshold  # True si el dedo está presionando
    
    # Detectar transición de inactivo a activo
    if current_active and not note_states[note]:
        notes[note].play()

    
    # Actualizar estado para el próximo frame
    note_states[note] = current_active
    
    # Visualización
    color = (0, 0, 255) if current_active else (0, 255, 0)
    cv2.circle(frame, (tip_x, tip_y), 10, color, -1)
    cv2.putText(frame, note, (tip_x - 20, tip_y - 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

def process_hand(hand_landmarks, hand_label, frame, w, h):
    """Procesa todos los dedos de una mano"""
    mapping = LEFT_HAND_MAPPING if hand_label == "Left" else RIGHT_HAND_MAPPING
    for finger, note in mapping.items():
        process_finger_note(frame, finger, note, hand_landmarks, w, h)
        

def main():
    # Configuración de MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=2,
        min_detection_confidence=0.9,
        min_tracking_confidence=0.9
    )
    
    # Configurar cámara
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    # Ventana a pantalla completa
    cv2.namedWindow('Piano Virtual', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Piano Virtual', cv2.WND_PROP_FULLSCREEN, 1)
    
    while cap.isOpened():

        success, frame = cap.read()
        if not success:
            continue
        
        # Espejo y conversión de color
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        h, w = frame.shape[:2]
        
        # Procesar manos detectadas
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, 
                results.multi_handedness
            ):
                label = handedness.classification[0].label
                process_hand(hand_landmarks, label, frame, w, h)
        
        # Mostrar FPS
        cv2.putText(frame, "ESC para salir", (10, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        cv2.imshow('Piano Virtual', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()