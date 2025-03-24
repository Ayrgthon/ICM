# main.py
from engine import SpeechEngine
from commands import CaptionModel, handle_command
import cv2  # Para abrir la cámara y tomar la foto
from huggingface_hub import login

# Ingresa tu token de Hugging Face
token = "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"
login(token)

def capture_image():
    # Abrir la cámara
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo acceder a la cámara.")
        return None

    # Tomar una foto
    print("Tomando la foto...")
    ret, frame = cap.read()
    if ret:
        # Guardar la imagen capturada
        image_path = "captured_image.jpg"
        cv2.imwrite(image_path, frame)
        print(f"Foto tomada y guardada en {image_path}")
        return image_path
    else:
        print("No se pudo capturar la imagen.")
        return None
    cap.release()

def main():
    # 1) Crear el engine de voz
    vosk_model_path = r"vosk-model-en-us-0.22"
    engine = SpeechEngine(model_path=vosk_model_path)

    # 2) Cargar el modelo de captioning usando PaliGemma
    caption_model = CaptionModel(model_path="google/paligemma-3b-pt-224")  # Cambié a PaliGemma

    print("[Main] Comenzando escucha. Di 'describe' para generar caption, 'salir' para terminar.")

    try:
        while True:
            recognized = engine.listen_once()  # Escuchar un comando
            if recognized:
                print(f"[Main] Reconocido: {recognized}")
                
                # Si "describe" está en la entrada (puede ser parte de una oración o frase)
                if "describe" in recognized.lower():
                    # El prompt será la entrada completa del usuario
                    prompt = recognized  # Usamos todo el texto que el usuario diga como prompt
                    
                    # Capturar la imagen de la cámara
                    image_path = capture_image()
                    if image_path:
                        caption = caption_model.generate_caption(
                            image_path=image_path,
                            prompt=prompt,  # Usar el prompt hablado (ahora puede ser cualquier cosa que contenga 'describe')
                            max_length=300
                        )
                        print("[Commands] Generated caption:", caption)
                
                elif recognized.lower() == "salir":
                    print("[Main] Salir solicitado.")
                    break
                else:
                    # Comando no reconocido
                    print("[Commands] Comando no reconocido:", recognized)
    except KeyboardInterrupt:
        print("[Main] Interrumpido con Ctrl+C.")
    finally:
        engine.close()  # Cerrar el engine de voz cuando se termine

if __name__ == "__main__":
    main()
