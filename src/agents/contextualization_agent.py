from openai import OpenAI
from src.prompts import CONTEXTUALIZATION_SYSTEM_PROMPT, CONTEXTUALIZATION_USER_TEMPLATE

from langfuse import observe, get_client

langfuse = get_client()

class ContextualizationAgent:

    def __init__(self, model_name: str = "gpt-4o"):
        self.client = OpenAI()
        self.model_name = model_name

    @observe(as_type="agent", name="Extraction Agent")
    def run(self, original_text: str, amendment_text: str) -> str:

        user_content = CONTEXTUALIZATION_USER_TEMPLATE.format(
            original_contract=original_text,
            amendment_contract=amendment_text,
        )

        return self._generate_contextualization(
            messages=[
                {"role": "system", "content": CONTEXTUALIZATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )

    @observe(as_type="generation", name="Amendment Contextualization")
    def _generate_contextualization(self, **kwargs) -> str:
        kwargs_clone = kwargs.copy()
        messages = kwargs_clone.pop("messages", None)

        langfuse.update_current_generation(
            input=messages, model=self.model_name, metadata=kwargs_clone
        )

        response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, **kwargs_clone
        )

        if response.usage:
            langfuse.update_current_generation(
                output=response.choices[0].message.content,
                usage_details={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                }
            )
        return response.choices[0].message.content or ""