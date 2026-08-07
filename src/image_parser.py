import base64
import mimetypes
import os
from openai import OpenAI
from src.prompts import VISION_OCR_PROMPT

from langfuse import observe, get_client

langfuse = get_client()

@observe(as_type="tool", name="Image Base64 Parser")
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

@observe(as_type="generation", name="GPT-4o Vision Processing")
def parse_contract_image(image_path: str) -> str:
    """Lee una imagen de contrato/enmienda y extrae su texto completo mediante GPT-4o"""
    base64_image, mime_type = encode_image_to_base64(image_path)
    client = OpenAI()

    messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": VISION_OCR_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        },
                    },
                ],
            }
        ]

    langfuse.update_current_generation(
        input=[{"type": "text", "text": VISION_OCR_PROMPT}, {"image_path": image_path}],
        model="gpt-4o",
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.2,
    )

    extracted_text = response.choices[0].message.content or ""

    if response.usage:
        langfuse.update_current_generation(
            output=extracted_text,
            usage_details={
                "input": response.usage.prompt_tokens,
                "output": response.usage.completion_tokens,
                "total": response.usage.total_tokens,
            },
        )

    return extracted_text