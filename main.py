# main.py

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import torch
from PIL import Image
from transformers import VisionEncoderDecoderModel, AutoTokenizer, ViTImageProcessor
import io

app = FastAPI()

# Carga del modelo (puedes extraerlo a un módulo aparte si quieres)
device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = "ViTGP"  # Ajusta con tu carpeta de fine-tuning
model = VisionEncoderDecoderModel.from_pretrained(model_path).to(device)
tokenizer = AutoTokenizer.from_pretrained(model_path)
feature_extractor = ViTImageProcessor.from_pretrained(model_path)

model.eval()

@app.get("/")
def root():
    return {"message": "API de Captioning activa"}

@app.post("/caption")
async def caption_image(file: UploadFile = File(...)):
    """
    Endpoint que recibe la imagen por 'file' y retorna el caption en JSON.
    """
    # 1) Leemos el contenido del archivo en memoria
    image_bytes = await file.read()

    # 2) Abrimos la imagen con PIL
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # 3) Preprocesar la imagen
    pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values.to(device)

    # 4) Generar el caption
    with torch.no_grad():
        output_ids = model.generate(pixel_values, max_length=50, num_beams=4)
    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # 5) Retornamos en un JSON
    return JSONResponse({"caption": caption})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
