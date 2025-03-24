# commands.py
import torch
from PIL import Image
from transformers import AutoProcessor, PaliGemmaForConditionalGeneration

class CaptionModel:
    def __init__(self, model_path="google/paligemma-3b-pt-224", device=None):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = device
        print(f"Usando el dispositivo: {self.device}")
        print(f"[Commands] Cargando modelo de Captioning desde: {model_path}")

        # Cargar el modelo PaliGemma y el procesador
        self.model = PaliGemmaForConditionalGeneration.from_pretrained(model_path).to(self.device).eval()
        self.processor = AutoProcessor.from_pretrained(model_path)

        print("[Commands] Modelo de Captioning cargado correctamente.")

    def generate_caption(self, image_path, prompt="Describe this image in great detail.", max_length=300):
        # Abrir y preprocesar la imagen
        img = Image.open(image_path).convert("RGB")
        
        # Agregar el token <image> al inicio del texto para cumplir con el formato que requiere PaliGemma
        text_input = "<image> " + prompt
        
        # Preprocesar la imagen y el texto
        inputs = self.processor(images=img, text=text_input, return_tensors="pt").to(self.device)

        # Realizar la inferencia en la GPU
        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs, 
                max_length=max_length,
                num_beams=4,  # Ajustar el número de haces (beams)
                do_sample=False
            )

        caption = self.processor.decode(output_ids[0], skip_special_tokens=True)
        return caption

def handle_command(command_str, caption_model):
    """
    Procesa el comando de texto reconocido.
    Por ejemplo, si es 'describe', llamamos a generate_caption(...).
    """
    # Quita espacios y pasa a minúsculas
    cmd = command_str.strip().lower()

    if cmd == "describe":
        print("[Commands] Comando 'describe' recibido.")
        return True  # La cámara ya toma la foto en main.py y genera la descripción.

    elif cmd == "salir":
        print("[Commands] Recibido 'salir'")
        return False  # Indica que hay que finalizar

    else:
        # Comando no reconocido
        print("[Commands] Comando no reconocido:", command_str)
        return True  # Seguimos escuchando
