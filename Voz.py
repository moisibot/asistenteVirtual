import speech_recognition as sr
import os
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import soundcard as sc
import numpy as np
import wave
import subprocess
import platform

def speak(text):
    tts = gTTS(text=text, lang='es')
    filename = "output.mp3"
    tts.save(filename)
    sound = AudioSegment.from_mp3(filename)
    play(sound)
    os.remove(filename)

def listen_command():
    duration = 5
    fs = 44100
    channels = 1
    filename = "output.wav"

    print("Escuchando...")
    mic = sc.default_microphone()
    with mic.recorder(samplerate=fs) as mic:
        data = mic.record(numframes=int(duration * fs))

    print("Grabación terminada")

    if data.shape[1] > 1:
        data = np.mean(data, axis=1)

    data = (data / np.max(np.abs(data)) * 32767).astype(np.int16)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(data.tobytes())

    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)

    try:
        command = recognizer.recognize_google(audio, language="es-ES")
        print(f"Has dicho: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("No he podido entender el audio")
        return ""
    except sr.RequestError:
        print("No se pudo solicitar resultados al servicio de reconocimiento de voz")
        return ""
    finally:
        os.remove(filename)

def open_folder(folder_name):
    home_dir = os.path.expanduser("~")

    common_folders = {
        "documentos": "Documentos",
        "descargas": "Descargas",
        "música": "Música",
        "imágenes": "Imágenes",
        "vídeos": "Vídeos",
        "escritorio": "Escritorio",
    }

    if folder_name in common_folders:
        folder_name = common_folders[folder_name]

    folder_path = os.path.join(home_dir, folder_name)

    print(f"Intentando abrir la carpeta: {folder_path}")

    if os.path.exists(folder_path):
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", folder_path])
            else:  # Linux y otros
                subprocess.Popen(["xdg-open", folder_path])
            speak(f"Abriendo la carpeta {folder_name}")
        except Exception as e:
            print(f"Error al abrir la carpeta: {e}")
            speak(f"Lo siento, hubo un error al abrir la carpeta {folder_name}")
    else:
        print(f"La carpeta no existe: {folder_path}")
        speak(f"Lo siento, no pude encontrar la carpeta {folder_name}")

def execute_command(command):
    print(f"Ejecutando comando: {command}")
    if "abrir" in command:
        folder_name = command.split("abrir")[-1].strip()
        open_folder(folder_name)
    elif "que hora es" in command:
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        speak(f"Son las {current_time}")
    elif "chiste" in command:
        speak("¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.")
    elif "listar carpetas" in command:
        home_dir = os.path.expanduser("~")
        folders = [f for f in os.listdir(home_dir) if os.path.isdir(os.path.join(home_dir, f))]
        speak("Las carpetas en tu directorio de inicio son: " + ", ".join(folders))
    else:
        speak("Lo siento, no entiendo ese comando.")

def main():
    speak("Hola, soy tu asistente virtual. Di 'hola' para activarme.")

    while True:
        command = listen_command()
        if command:
            print(f"Comando reconocido: {command}")
            if "hola" in command:
                speak("Hola, ¿en qué puedo ayudarte?")
                while True:
                    command = listen_command()
                    if command:
                        print(f"Comando reconocido: {command}")
                        if "adiós" in command:
                            speak("Hasta luego")
                            break
                        execute_command(command)
            elif "salir" in command:
                speak("Hasta luego")
                break

if __name__ == "__main__":
    main()