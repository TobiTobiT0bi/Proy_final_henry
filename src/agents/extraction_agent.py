from openai import OpenAI
from src.models import ContractChangeOutput
from src.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_TEMPLATE

class ExtractionAgent:

    def __init__(self, model_name: str = "gpt-4o"):
        self.client = OpenAI()
        self.model_name = model_name

    def run(self, original_text: str, amendment_text: str, context_map: str) -> ContractChangeOutput:

        user_content = EXTRACTION_USER_TEMPLATE.format(
            context_map=context_map,
            original_contract=original_text,
            amendment_contract=amendment_text,
        )

        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_format=ContractChangeOutput,
            temperature=0.0,
        )
        choice = response.choices[0].message

        if choice.refusal:
            raise ValueError(f"El modelo rechazó procesar la solicitud: {choice.refusal}")
        if not choice.parsed:
            raise ValueError("El modelo no devolvió un objeto validado por Pydantic.")

        return choice.parsed