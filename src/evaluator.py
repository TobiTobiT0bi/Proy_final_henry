import os
import json
from dotenv import load_dotenv
from pathlib import Path
from langfuse import Langfuse
from src.models import ContractChangeOutput

from langfuse import observe

load_dotenv()
langfuse_client = Langfuse()

CATEGORIES = ["standard", "variant", "boundary"]
GOLDEN_DIR = Path("data/golden_cases")


def _is_field_populated(value) -> bool:
    """Verifica si GPT-4o Vision logró extraer un valor útil.

    Devuelve False si el valor es None, lista/dict vacío, o un texto evasivo/nulo.
    """
    if value is None:
        return False
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) > 0
    if isinstance(value, str):
        cleaned = value.strip().lower()
        null_responses = {
            "",
            "n/a",
            "none",
            "null",
            "no especificado",
            "sin información",
            "unknown",
            "no detectado",
        }
        return cleaned not in null_responses
    if isinstance(value, (int, float, bool)):
        return True
    return False


def _score_single_case(output_dict: dict, expected: dict) -> tuple[float, float]:
    """Evalúa la tasa de extracción (Accuracy) y la presencia del esquema (Completeness).

    - Accuracy: Proporción de campos esperados donde GPT-4o Vision extrajo información válida.
    - Completeness: Proporción de claves del esquema presentes en el diccionario de salida.
    """
    if not expected:
        return 0.0, 0.0

    target_keys = [k for k in expected.keys() if k != "id"]
    if not target_keys:
        return 0.0, 0.0

    keys_present = sum(1 for k in target_keys if k in output_dict)
    completeness = keys_present / len(target_keys)

    extracted_fields = sum(
        1 for k in target_keys
        if k in output_dict and _is_field_populated(output_dict[k])
    )
    accuracy = extracted_fields / len(target_keys)

    return accuracy, completeness

@observe(as_type="evaluator", name="Golden Cases Evaluator")
def evaluate_with_best_archetype(
    output: ContractChangeOutput, trace_id: str | None = None
) -> dict:
    """1. Carga cada uno de los 3 archivos JSON (standard.json, variant.json, boundary.json).
    2. Evalúa la capacidad de extracción de GPT-4o Vision en los 5 casos de cada archivo.
    3. Selecciona la categoría relevante y genera las métricas consolidadas.
    4. Envía métricas a Langfuse usando create_score().
    """
    output_dict = output.model_dump()
    category_results = {}

    for category in CATEGORIES:
        json_file = GOLDEN_DIR / f"{category}.json"
        if not json_file.exists():
            continue

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                cases_list = json.load(f)

            if not isinstance(cases_list, list):
                continue

            case_scores = []
            for item in cases_list:
                acc, comp = _score_single_case(output_dict, item)
                case_scores.append({
                    "id": item.get("id", "case_unknown"),
                    "accuracy": acc,
                    "completeness": comp,
                })

            if case_scores:
                avg_acc = sum(c["accuracy"] for c in case_scores) / len(case_scores)
                avg_comp = sum(c["completeness"] for c in case_scores) / len(case_scores)
                max_acc = max(c["accuracy"] for c in case_scores)

                category_results[category] = {
                    "avg_accuracy": avg_acc,
                    "avg_completeness": avg_comp,
                    "max_accuracy": max_acc,
                    "cases": case_scores,
                }
        except Exception as e:
            print(f"⚠️ Error leyendo {json_file}: {e}")

    if not category_results:
        return {"valid": False, "error": "No se encontraron los archivos JSON en data/golden_cases/"}

    best_category = max(
        category_results.keys(),
        key=lambda cat: category_results[cat]["max_accuracy"],
    )
    selected_data = category_results[best_category]

    trace_url = None
    if trace_id:
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/")
        trace_url = f"{host}/trace/{trace_id}"

    if trace_id:
        try:
            langfuse_client.create_score(
                trace_id=trace_id,
                name="pydantic_schema_valid",
                value=1,
                data_type="BOOLEAN",
                comment="Schema Pydantic válido",
            )
            langfuse_client.create_score(
                trace_id=trace_id,
                name="selected_golden_type",
                value=best_category,
                data_type="CATEGORICAL",
                comment=f"Tipo de archivo Golden seleccionado: {best_category}.json",
            )
            langfuse_client.create_score(
                trace_id=trace_id,
                name=f"extraction_rate_{best_category}_avg",
                value=round(selected_data["avg_accuracy"], 2),
                comment=f"Tasa de extracción promedio en los 5 casos de {best_category}.json",
            )
            langfuse_client.create_score(
                trace_id=trace_id,
                name=f"completeness_{best_category}_avg",
                value=round(selected_data["avg_completeness"], 2),
                comment=f"Completeness promedio en los 5 casos de {best_category}.json",
            )
            langfuse_client.flush()
        except Exception as e:
            print(f"⚠️ Error enviando métricas a Langfuse: {e}")

    return {
        "valid": True,
        "selected_category": best_category,
        "avg_accuracy": selected_data["avg_accuracy"],
        "avg_completeness": selected_data["avg_completeness"],
        "cases_detailed": selected_data["cases"],
        "all_categories_summary": category_results,
        "trace_url": trace_url,
    }