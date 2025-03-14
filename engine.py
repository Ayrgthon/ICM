# engine.py
import pyaudio
import json
from vosk import Model as VoskModel, KaldiRecognizer

class SpeechEngine:
    def __init__(self, model_path, rate=16000, chunk=4096, channels=1):
        """
        Inicializa el modelo de Vosk y el flujo de audio (PyAudio).
        """
        print(f"[Engine] Cargando modelo Vosk desde: {model_path}")
        self.model = VoskModel(model_path)
        self.rate = rate
        self.chunk = chunk
        self.channels = channels
        self._p = pyaudio.PyAudio()

        # Configurar stream de micrófono
        self.stream = self._p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.recognizer = KaldiRecognizer(self.model, self.rate)
        print("[Engine] Modelo Vosk cargado y micrófono listo.")

    def listen_once(self):
        """
        Lee un chunk de audio y retorna el texto final si se detecta una frase completa,
        o None si todavía no hay una frase completa.
        """
        data = self.stream.read(self.chunk, exception_on_overflow=False)
        if self.recognizer.AcceptWaveform(data):
            result_json = self.recognizer.Result()
            result_dict = json.loads(result_json)
            recognized_text = result_dict.get("text", "").strip().lower()
            return recognized_text if recognized_text else None
        else:
            # partial_result = self.recognizer.PartialResult()
            # si lo deseas, podrías procesar resultados parciales
            return None

    def close(self):
        """
        Detiene y cierra el stream de audio.
        """
        print("[Engine] Cerrando SpeechEngine...")
        self.stream.stop_stream()
        self.stream.close()
        self._p.terminate()
