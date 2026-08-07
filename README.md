# Proyecto final Henry
## Legal Contract Amendment Extractor & Evaluator

Este proyecto implementa una arquitectura multi-agente basada en **GPT-4o Vision** e **Ingeniería de Prompts** para la extracción, análisis comparativo y estructuración de cambios entre dos versiones de un contrato legal (contrato original vs. contrato modificado/enmienda).

El sistema procesa imágenes de documentos contractuales, analiza las diferencias cláusula por cláusula, valida la información mediante esquemas **Pydantic**, instrumenta trazabilidad completa en **Langfuse** y evalúa la calidad de la extracción frente a un dataset de referencia (*Golden Cases*).

---

## 🏗️ Arquitectura del Sistema

El pipeline procesa las imágenes en una secuencia de etapas desacopladas:


```

[Imágenes del Contrato]
│
▼
[Image Parser (GPT-4o Vision)] ──► Extrae texto crudo y formato visual de ambos documentos
│
▼
[Agente 1: Contextualización]  ──► Compara cláusula por cláusula e identifica cambios sustanciales
│
▼
[Agente 2: Extracción]         ──► Estructura los cambios según el modelo Pydantic ContractChangeOutput
│
▼
[Evaluador & Langfuse]         ──► Mide el Extraction Success Rate vs Golden Cases y reporta la traza

```

### Componentes Principales

1. **`src/image_parser.py`**: Codifica las imágenes en Base64, valida formatos e invoca GPT-4o Vision para digitalizar con fidelidad el texto de los contratos.
2. **`src/agents/contextualization_agent.py` (Agente 1)**: Analiza el contexto de ambos documentos, compara las diferencias (precios, plazos, condiciones) y genera una síntesis narrativa del cambio contractual.
3. **`src/agents/extraction_agent.py` (Agente 2)**: Toma el análisis contextual e impone un esquema rígido usando Structured Outputs de OpenAI y modelos Pydantic.
4. **`src/models.py`**: Define el modelo `ContractChangeOutput` garantizando los tipos de datos requeridos (`contract_type`, `modified_clauses`, `summary_of_the_change`).
5. **`src/evaluator.py`**: Calcula métricas de desempeño (**Tasa de Extracción / Accuracy** y **Completeness del Esquema**) comparando la salida contra los arquetipos almacenados en `data/golden_cases/`.
6. **Integración Langfuse**: Instrumentación mediante decoradores `@observe` para trazabilidad jerárquica (spans, latencias, tokens) y envío de puntuaciones (`create_score`).

---

## 🚀 Requisitos Previos e Instalación

Este proyecto utiliza [uv](https://github.com/astral-sh/uv) como gestor de paquetes de alto rendimiento en Python.

### 1. Clonar el repositorio y configurar el entorno
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>

# Crear entorno e instalar dependencias usando uv
uv sync

```

*(Opcional: Si preferís pip tradicional, podés ejecutar `pip install -r requirements.txt`)*

### 2. Configurar Variables de Entorno

Copiá el archivo de ejemplo `.env.example` a `.env` y completá con tus llaves de API:

```bash
cp .env.example .env

```

Configuración en `.env`:

```env
OPENAI_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=[https://cloud.langfuse.com](https://cloud.langfuse.com)

```

---

## 💻 Uso del Pipeline

Para ejecutar el pipeline pasando dos rutas de imágenes de contrato como argumento:

```bash
uv run python src/main.py data/test_contracts/documento_1__contrato.jpg data/test_contracts/documento_1__enmienda.jpg

```

### Salida esperada en consola:

* Resumen formateado en consola con el tipo de contrato, cláusulas modificadas y el resumen del cambio.
* Reporte detallado del `Evaluator` mostrando la Tasa de Extracción (*Accuracy*) y la cobertura (*Completeness*).
* Enlace directo al Trace generado en el dashboard de **Langfuse**.

---

## 🛠️ Decisiones Técnicas y Evaluaciones

* **Aislamiento Multi-agente:** Separar la comparación contextual (Agente 1) de la estructuración en Pydantic (Agente 2) reduce alucinaciones y mejora la consistencia del output final.
* **Métrica de Extracción (Accuracy):** El evaluador analiza si GPT-4o Vision fue capaz de poblar campos con contenido válido (discriminando `None`, respuestas evasivas como `"N/A"` o cadenas vacías).
* **Trazabilidad:** Toda llamada a GPT-4o e iteración de agentes genera Spans jerárquicos en Langfuse para auditoría de costos, latencia y observabilidad de prompts.