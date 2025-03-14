# main.py
from engine import SpeechEngine
from commands import CaptionModel, handle_command

def main():
    # 1) Crear el engine de voz
    vosk_model_path = r"vosk-model-es-0.42"
    engine = SpeechEngine(model_path=vosk_model_path)

    # 2) Cargar el modelo de captioning
    caption_model = CaptionModel(model_path="ViTGP")  # Ajusta la ruta si es distinto

    print("[Main] Comenzando escucha. Di 'describe' para generar caption, 'salir' para terminar.")

    try:
        while True:
            recognized = engine.listen_once()
            if recognized:
                print(f"[Main] Reconocido: {recognized}")
                # Manejar el comando
                keep_going = handle_command(recognized, caption_model)
                if not keep_going:
                    # 'False' => se solicitó 'salir'
                    break
    except KeyboardInterrupt:
        print("[Main] Interrumpido con Ctrl+C.")
    finally:
        engine.close()

if __name__ == "__main__":
    main()
