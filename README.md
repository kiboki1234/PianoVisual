# Virtual Piano Game

¡Bienvenido al Virtual Piano Game!  
Este proyecto es un juego interactivo en el que puedes tocar notas de piano usando movimientos de la mano. Utiliza **MediaPipe** para la detección de manos, **OpenCV** para el procesamiento de video y **Pygame** para la reproducción de audio, combinados con efectos visuales como partículas y animaciones de combo.

## Descripción

El juego muestra notas que "caen" desde la parte superior de la pantalla y el jugador debe "tocar" las notas usando sus dedos, detectados a través de la cámara web. Al tocar una nota correctamente, se reproducirá el sonido correspondiente y se generarán efectos visuales (como partículas y un borde animado) que resaltan los combos y aumentan la puntuación. Además, el juego cuenta con una cuenta regresiva inicial y una pantalla final de felicitaciones con la puntuación final.

## Características

- **Detección de manos en tiempo real:**  
  Utiliza MediaPipe para identificar la posición de los dedos y detectar colisiones con las notas en caída.

- **Reproducción de audio:**  
  Cada nota está asociada a un archivo de audio reproducido con baja latencia usando Pygame.

- **Efectos visuales dinámicos:**  
  - Partículas que se generan al tocar una nota.
  - Animación de borde pulsante y mensajes de combo cuando se encadenan aciertos.
  - Pantalla final con mensaje de felicitaciones y la puntuación final.

- **Interfaz interactiva:**  
  Incluye una cuenta regresiva antes de comenzar y controles simples (tecla ESC para salir).

## Requisitos

- Python 3.6 o superior
- [Pygame](https://www.pygame.org/)
- [OpenCV](https://opencv.org/) (`opencv-python`)
- [MediaPipe](https://mediapipe.dev/)
- [NumPy](https://numpy.org/) *(opcional, pero recomendable para algunos cálculos)*

## Instalación

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/tu_usuario/virtual-piano-game.git
   cd virtual-piano-game
   ```

2. **Instalar las dependencias:**

   ```bash
   pip install pygame opencv-python mediapipe
   ```

3. **Agregar los archivos de audio:**

   Coloca los archivos de audio (por ejemplo, `Do.mp3`, `Re.mp3`, etc.) en la carpeta `AudiosPiano` dentro del directorio del proyecto.

## Uso

Ejecuta el juego con:

```bash
python pianoVisualInteractivo.py
```

- **Cuenta regresiva:**  
  Se inicia con una cuenta regresiva de 3 segundos para preparar al jugador.
  
- **Jugabilidad:**  
  Las notas caen desde la parte superior y se deben tocar con la mano.  
  Cada acierto incrementa la puntuación y, si se encadenan aciertos rápidos, se activa un combo que multiplica los puntos.

- **Efectos visuales:**  
  Al tocar una nota, se generan partículas y un borde animado que varía en color, aumentando la inmersión y la sensación de logro.

- **Salir:**  
  Presiona la tecla `ESC` para salir en cualquier momento.

## Otro modo de juego

Si prefieres una experiencia diferente, donde puedas tocar las notas del piano libremente sin esperar a que caigan, puedes probar este otro código que permite tocar notas de manera interactiva detectando la presión de los dedos:

[Código de Piano Interactivo](pianoVisual.py)

```bash
python pianoVisual.py
```
Este modo permite activar las notas manualmente moviendo los dedos sobre la cámara sin necesidad de esperar la aparición de notas en pantalla.

## Capturas de Pantalla

*Agrega aquí capturas de pantalla o GIFs del juego en acción para mostrar lo llamativo y dinámico que es.*

## Contribuciones

¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar el juego o deseas añadir nuevas características, siéntete libre de abrir un issue o enviar un pull request.

## Licencia

Este proyecto se distribuye bajo la [MIT License](LICENSE).

---

¡Disfruta tocando el Virtual Piano y mejora tu puntería musical con cada combo!

