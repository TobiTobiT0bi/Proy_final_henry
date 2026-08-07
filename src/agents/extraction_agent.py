from openai import OpenAI
from src.models import ContractChangeOutput
from src.prompts import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_TEMPLATE

from langfuse import observe, get_client

langfuse = get_client()

class ExtractionAgent:

    def __init__(self, model_name: str = "gpt-4o"):
        self.client = OpenAI()
        self.model_name = model_name

    @observe(as_type="agent", name="Extraction Agent")
    def run(self, original_text: str, amendment_text: str, context_map: str) -> ContractChangeOutput:

        user_content = EXTRACTION_USER_TEMPLATE.format(
            context_map=context_map,
            original_contract=original_text,
            amendment_contract=amendment_text,
        )
        return self._generate_extraction(
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_format=ContractChangeOutput,
            temperature=0.0,
        )
    
    @observe(as_type="generation", name="Amendment extraction")
    def _generate_extraction(self,**kwargs) -> ContractChangeOutput:
        kwargs_clone = kwargs.copy()
        messages = kwargs_clone.pop("messages", None)

        kwargs_clone.pop("response_format", None)

        langfuse.update_current_generation(
            input=messages,
            model=self.model_name,
            metadata={
                **kwargs_clone,
                "response_format": "ContractChangeOutput",
            },
        )

        response = self.client.beta.chat.completions.parse(
            model=self.model_name,
            response_format=ContractChangeOutput,
            messages=messages,
            **kwargs_clone,
        )

        extracted_output = response.choices[0].message.parsed

        if response.usage:
            langfuse.update_current_generation(
                output=extracted_output.model_dump() if extracted_output else None,
                usage_details={
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                },
            )

        return extracted_output