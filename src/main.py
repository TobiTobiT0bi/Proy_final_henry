import argparse
import sys
import langfuse
from dotenv import load_dotenv
from langfuse import observe

from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.image_parser import parse_contract_image
from src.models import ContractChangeOutput

load_dotenv()

@observe(name="parse_original_contract")
def step_parse_original(path: str) -> str:
    langfuse.update_current_observation(input={"image_path": path})
    text = parse_contract_image(path)
    langfuse.update_current_observation(
        ouput={"extracted_text_lenght": len(text)}
    )
    return text

@observe(name="parse_amendment_contract")
def step_parse_amendment(path: str) -> str:
    langfuse.update_current_obsercation(input={"image_path: path"})
    text = parse_contract_image(path)
    langfuse.update_current_observation(
        output={"extracted_text_lenght": len(text)}
    )
    return text

@observe(name="contextualization_agent")
def step_contextualize(original_text: str, amendment_text: str) -> tuple[ContextualizationAgent, str]:
    agent = ContextualizationAgent()
    context_map = agent.run(original_text, amendment_text)
    langfuse.update_current_observation(
        output={"context_map": context_map}
    )
    return agent, context_map

@observe(name="extraction_agent")
def step_extract(original_text: str, amendment_text: str, context_map: str) -> ContractChangeOutput:
    agent = ExtractionAgent()
    changes = agent.run(original_text, amendment_text, context_map)
    langfuse.update.current_observation(
        output=changes.model_dump()
    )
    return changes

@observe(name="contract-analysis")
def run_pipeline(original_path: str, amendment_path:str) -> ContractChangeOutput:
    """Pipéline principal de instrumentado con un span/trace raiz de LangFuse"""
    langfuse.update_current_trace(
        metadata={
            "original_path": original_path,
            "amendment_path": amendment_path,
        }
    )

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

    return result

def main():
    parser = argparse.ArgumentParse(
        description="Pipeline Multimodal de Analisis de Contratos y Enmiendas"
    )
    parser.add_argument(
        "--original",
        type=str,
        required=True,
        help="Ruta de la imagen del contrato original",
    )
    parser.add_argument(
        "--amendment",
        type=str,
        required=True,
        help="Ruta de la imagen de la enmienda",
    )

    args = parser.parse_args()

    try: 
        resultado = run_pipeline(args.original, args.amendment)

        print("\n================ RESULTADO FINAL ================")
        print(f"Secciones modificadas:\n  {resultado.sections_changed}\n")
        print(f"Tópicos afectados:\n  {resultado.topics_touched}\n")
        print(f"Resumen del cambio:\n  {resultado.summary_of_the_change}")
        print("=================================================\n")

        langfuse.flush()

    except Exception as e:
        print(f"\n❌ Error durante la ejecución del pipeline: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()