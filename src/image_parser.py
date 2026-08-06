import base64
import mimetypes
import os
from openai import OpenAI

client = OpenAI

def encode_image_to_base64(image_path: str) -> tuple[str, str]:
    """Valida la existencia de la imagen y la codifica a base64 junto con su MIME type"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No se encontró la imagen en la ruta: {image_path}")
    
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type not in ["image/jpeg", "image/png"]:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    return encoded_string, mime_type
