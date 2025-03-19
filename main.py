from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import shutil
import json
from typing import Optional
from commands import CaptionModel, handle_command
from vosk import Model as VoskModel, KaldiRecognizer

app = FastAPI(title="Image Caption API")

# Inicializar el modelo de captioning al iniciar la API
caption_model = CaptionModel(model_path="ViTGP")

# Inicializar el modelo de reconocimiento de voz
vosk_model_path = r"vosk-model-es-0.42"
vosk_model = VoskModel(vosk_model_path)
recognizer = KaldiRecognizer(vosk_model, 16000)

@app.post("/process_command/")
async def process_command(
    audio: UploadFile = File(None),
    command_text: str = Form(None),
    image: UploadFile = File(None)
):
    """
    Endpoint para procesar comandos.
    Puedes enviar un comando como texto O un archivo de audio para ser reconocido.
    Si el comando es 'describe', también debes enviar una imagen.
    """
    # Verificar que se haya proporcionado un comando (texto) o un archivo de audio
    if not audio and not command_text:
        return JSONResponse(
            status_code=400,
            content={"error": "Debes proporcionar un comando de texto o un archivo de audio"}
        )
    
    # Si se envió audio, reconocer el texto
    if audio:
        try:
            # Guardar el archivo de audio temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                shutil.copyfileobj(audio.file, temp_audio)
                temp_audio_path = temp_audio.name
            
            # Procesar el archivo de audio con Vosk
            with open(temp_audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
                
            # Procesar audio con Vosk
            if recognizer.AcceptWaveform(audio_data):
                result_json = recognizer.Result()
                result_dict = json.loads(result_json)
                recognized_text = result_dict.get("text", "").strip().lower()
            else:
                recognized_text = ""
                
            # Limpiar archivo temporal
            os.unlink(temp_audio_path)
            
            if not recognized_text:
                return JSONResponse(
                    status_code=400,
                    content={"error": "No se pudo reconocer ningún comando en el audio"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Error al procesar el audio: {str(e)}"}
            )
    else:
        # Usar el comando proporcionado como texto
        recognized_text = command_text.strip().lower()
    
    # Procesar el comando reconocido
    if recognized_text == "describe":
        # Si el comando es 'describe', necesitamos una imagen
        if not image:
            return JSONResponse(
                status_code=400,
                content={"error": "Para el comando 'describe' se requiere una imagen"}
            )
        
        try:
            # Guardar la imagen temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
                shutil.copyfileobj(image.file, temp_image)
                temp_image_path = temp_image.name
            
            # Generar caption para la imagen
            caption = caption_model.generate_caption(
                image_path=temp_image_path,
                max_length=120,
                num_beams=4
            )
            
            # Limpiar archivo temporal
            os.unlink(temp_image_path)
            
            return {"command": recognized_text, "caption": caption}
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": f"Error al procesar la imagen: {str(e)}"}
            )
    
    elif recognized_text == "salir":
        return {"command": recognized_text, "message": "Comando 'salir' recibido"}
    
    else:
        return {"command": recognized_text, "message": f"Comando no reconocido: {recognized_text}"}

@app.get("/")
async def root():
    return {"message": "API de Reconocimiento de Comandos y Generación de Descripciones"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)