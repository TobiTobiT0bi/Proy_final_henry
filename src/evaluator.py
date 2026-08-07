import json
from pathlib import Path
from langfuse import Langfuse
from src.models import ContractChangeOutput

langfuse_client = Langfuse()

CATEGORIES = ["standard", "variant", "boundary"]
GOLDEN_DIR = Path("data/golden_cases")

def _score_single_case(output_dict: dict, expected: dict) -> tuple[float, float]:
    """Compara campo por campo omitiendo la llave 'id' del Golden Case."""
    if not expected:
        return 0.0, 0.0

    target_keys = [k for k in expected.keys() if k != "id"]
    if not target_keys:
        return 0.0, 0.0

    correct_fields = sum(
        output_dict.get(k) == expected[k] for k in target_keys if k in output_dict
    )
    accuracy = correct_fields / len(target_keys)

    completeness = sum(k in output_dict for k in target_keys) / len(target_keys)

    return accuracy, completeness


def evaluate_with_best_archetype(output: ContractChangeOutput, trace_id: str) -> dict:
    """
    1. Carga cada uno de los 3 archivos JSON (standard.json, variant.json, boundary.json).
    2. Evalúa la salida contra la lista de 5 casos contenida en cada archivo.
    3. Selecciona el tipo de archivo con mayor afinidad e itera sobre sus 5 casos.
    4. Envía métricas consolidadas a Langfuse.
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

    if trace_id:
        print(f"subiendo scores con trace_id: {trace_id}")
        try:
            langfuse_client.create_score(
                trace_id=trace_id,
                name="pydantic_schema_valid",
                value=1.0,
                comment="Schema Pydantic válido",
            )
            langfuse_client.create_score(
                trace_id=trace_id,
                name="selected_golden_type",
                value=1.0,
                comment=f"Tipo de archivo Golden seleccionado: {best_category}.json",
            )
            langfuse_client.create_score(
                trace_id=trace_id,
                name=f"accuracy_{best_category}_avg",
                value=round(selected_data["avg_accuracy"], 2),
                comment=f"Accuracy promedio iterado en los 5 casos de {best_category}.json",
            )
            langfuse_client.create_score(
                trace_id=trace_id,
                name=f"completeness_{best_category}_avg",
                value=round(selected_data["avg_completeness"], 2),
                comment=f"Completeness promedio iterado en los 5 casos de {best_category}.json",
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
    }

