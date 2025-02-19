from pydub import AudioSegment

# Convertir los archivos a WAV
audio_files = ['Do.mp3', 'Re.mp3', 'Mi.mp3', 'Fa.mp3', 'Sol.mp3']
for file in audio_files:
    sound = AudioSegment.from_mp3(f"AudiosPiano/{file}")
    sound.export(f"AudiosPiano/{file.replace('.mp3', '.wav')}", format="wav")
