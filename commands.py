# commands.py
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, AutoTokenizer, ViTImageProcessor

class CaptionModel:
    def __init__(self, model_path="ViTGP", device=None):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device
        print(f"[Commands] Cargando modelo de Captioning desde: {model_path}")

        self.model = VisionEncoderDecoderModel.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.feature_extractor = ViTImageProcessor.from_pretrained(model_path)

        self.model.to(self.device)
        self.model.eval()
        print("[Commands] Modelo de Captioning cargado correctamente.")

    def generate_caption(self, image_path, max_length=30, num_beams=4):
        img = Image.open(image_path).convert("RGB")
        pixel_values = self.feature_extractor(images=img, return_tensors="pt").pixel_values.to(self.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                pixel_values,
                max_length=max_length,
                num_beams=num_beams
            )
        caption = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return caption

def handle_command(command_str, caption_model):
    """
    Procesa el comando de texto reconocido.
    Por ejemplo, si es 'describe', llamamos a generate_caption(...).
    """
    # Quita espacios y pasa a minúsculas
    cmd = command_str.strip().lower()

    if cmd == "describe":
        # Generar la descripción de una imagen fija, o tal vez una pasada como parámetro
        image_path = "B601743B-02FF-4B4F-B065-3B95473124D6-1030x773.jpeg"
        caption = caption_model.generate_caption(
            image_path=image_path,
            max_length=120,
            num_beams=4
        )
        print("[Commands] Generated caption:", caption)
        return True  # Indica que se manejó el comando

    elif cmd == "salir":
        print("[Commands] Recibido 'salir'")
        return False  # Indica que hay que finalizar

    else:
        # Comando no reconocido, podrías manejar más
        print("[Commands] Comando no reconocido:", command_str)
        return True  # Seguimos escuchando
