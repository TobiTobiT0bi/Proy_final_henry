from openai import OpenAI
from src.prompts import CONTEXTUALIZATION_SYSTEM_PROMPT, CONTEXTUALIZATION_USER_TEMPLATE

class ContextualizationAgent:

    def __init__(self, model_name: str = "gpt-4o"):
        self.client = OpenAI()
        self.model_name = model_name

    def run(self, original_text: str, amendment_text: str) -> str:

        user_content = CONTEXTUALIZATION_USER_TEMPLATE.format(
            original_contract=original_text,
            amendment_contract=amendment_text,
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": CONTEXTUALIZATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2
        )

        return response.choices[0].message.content or ""