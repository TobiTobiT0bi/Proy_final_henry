import langfuse
from dotenv import load_dotenv
from langfuse import observe, Langfuse

from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.image_parser import parse_contract_image
from src.models import ContractChangeOutput
from src.cli import run_interactive_menu

load_dotenv()
langfuse_client = Langfuse()

@observe(name="parse_original_contract")
def step_parse_original(path: str) -> str:
    text = parse_contract_image(path)
    return text

@observe(name="parse_amendment_contract")
def step_parse_amendment(path: str) -> str:
    text = parse_contract_image(path)
    return text

@observe(name="contextualization_agent")
def step_contextualize(original_text: str, amendment_text: str) -> tuple[ContextualizationAgent, str]:
    agent = ContextualizationAgent()
    context_map = agent.run(original_text, amendment_text)
    return agent, context_map

@observe(name="extraction_agent")
def step_extract(original_text: str, amendment_text: str, context_map: str) -> ContractChangeOutput:
    agent = ExtractionAgent()
    changes = agent.run(original_text, amendment_text, context_map)
    return changes

@observe(name="contract-analysis")
def run_pipeline(original_path: str, amendment_path:str) -> ContractChangeOutput:
    """Pipeline principal de instrumentado con un span/trace raiz de LangFuse"""

    print("[1/4] Extrayendo texto del contrato original...")
    original_text = step_parse_original(original_path)

    print("[1/4] Extrayendo texto de la enmienda...")
    amendment_text = step_parse_amendment(amendment_path)

    print("[2/4] Ejecutando Agente 1 (Contextualización)...")
    _, context_map = step_contextualize(original_text, amendment_text)

    print("[3/4 y 4/4] Ejecutando Agente 2 (Extracción) y validación Pydantic...")
    result: ContractChangeOutput = step_extract(
        original_text, amendment_text, context_map
    )

    langfuse_client.flush()

    return result

def main():
    run_interactive_menu(pipeline_runner=run_pipeline)


if __name__ == "__main__":
    main()