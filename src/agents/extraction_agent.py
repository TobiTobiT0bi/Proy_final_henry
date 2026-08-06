from openai import OpenAI
from src.models import ContractChangeOutput
from src.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_TEMPLATE

class ExtractionAgent:

    def __init__(self, model_name: str = "gpt-4o"):
        self.client = OpenAI()
        self.model_name = model_name

    def run(self, original_text: str, amendment_text: str, context_map: str) -> ContractChangeOutput:
        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": EXTRACTION_USER_TEMPLATE},
            ],
            response_format=ContractChangeOutput,
            temperature=0.0,
        )

        return response.choices[0].message.parsed