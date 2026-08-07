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

Este proyecto utiliza **[uv](https://github.com/astral-sh/uv)** como gestor de paquetes de alto rendimiento en Python y **`make`** para simplificar la configuración y ejecución.

### 1. Setup Inicial

Para configurar el entorno por primera vez tras clonar el repositorio, simplemente ejecutá (EN BASH):

```bash
make setup
```

Este comando automatiza los siguientes pasos:

* Crea el archivo `.env` a partir de `.env.example` (si no existe previa ejecución).
* Sincroniza e instala todas las dependencias del proyecto usando `uv sync`.

### 2. Configurar Variables de Entorno

Antes de correr el pipeline, asegurate de cargar tus credenciales en el archivo `.env` recién creado:

```env
OPENAI_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com

```

---

## 💻 Uso del Pipeline

Podés ejecutar el análisis sobre los contratos de prueba por defecto mediante el comando:

```bash
make run
```

### Salida esperada en consola:

* Resumen formateado con el tipo de contrato, cláusulas modificadas y la síntesis narrativa del cambio.
* Reporte del `Evaluator` detallando las métricas de **Accuracy (Tasa de Extracción)** y **Completeness**.
* Enlace directo al **Trace de Langfuse** para auditoría y observabilidad.

---

## 🛠️ Decisiones Técnicas y Evaluaciones

### 1. Arquitectura Multi-Agente Desacoplada
En lugar de solicitar la extracción y estructuración directa en un solo paso (Single-Prompt), implementamos una arquitectura de dos agentes especializados:
* **Agente 1 (Contextualización):** Se enfoca puramente en la capacidad analítica y semántica del modelo GPT-4o para comparar cláusula por cláusula las diferencias contractuales.
* **Agente 2 (Extracción Estructurada):** Toma el análisis cualitativo previa y se enfoca exclusivamente en traducir esa información al esquema requerido.
Este desacoplamiento reduce drásticamente las alucinaciones y omisiones de cláusulas en contratos complejos.

---

### 2. Garantía de Esquema con Pydantic y Structured Outputs (`json_schema`)
Para garantizar que la salida sea 100% interoperable con sistemas downstream y cumpla con el modelo `ContractChangeOutput`, implementamos **Structured Outputs nativo de OpenAI**:
* **Garantía desde el API Call:** En lugar de relying únicamente en "prompt engineering" o parseos frágiles con expresiones regulares, configuramos el parámetro `response_format` en la llamada a la API pasando el esquema JSON generado por Pydantic.
* **Strict Validation:** Esto obliga al modelo a nivel de decodificación de tokens a generar una respuesta que respete exactamente los campos (`contract_type`, `modified_clauses`, `summary_of_the_change`), evitando campos nulos no deseados o estructuras corruptas.

---

### 3. Evaluación Guiada por Golden Cases
Para medir la efectividad real del pipeline en un entorno controlado y reproducible, diseñamos un dataset de referencia (*Golden Cases*):
* **Por qué Golden Cases:** En tareas de PLN y visión con contratos, la evaluación no se puede limitar a saber si la API devolvió un status 200. Necesitamos verificar que la extracción contenga exactamente las cláusulas modificadas reales (ground truth).
* **Cómo lo implementamos:** Creamos pares de prueba (`data/test_contracts/`) con sus correspondientes salidas esperadas en `data/golden_cases/`. El `Evaluator` ejecuta comparaciones sobre cada campo para calcular dos métricas clave:
  1. **Accuracy / Tasa de Extracción:** Mide el porcentaje de precisión en la identificación correcta de las cláusulas modificadas y tipo de contrato.
  2. **Completeness (Cobertura del Esquema):** Evalúa si el modelo pobló con contenido sustancial todos los campos requeridos, descartando respuestas evasivas (como `"N/A"`, `"no especificado"` o cadenas vacías).

---

### 4. Observabilidad y Trazabilidad con Langfuse
La integración de **Langfuse** nos otorga visibilidad total sobre la ejecución interna del pipeline multi-agente, resolviendo las limitaciones típicas del desarrollo con LLMs a ciegas.

#### ¿Por qué usar Langfuse vs. No Usarlo?

| Aspecto | Sin Observabilidad (Logs tradicionales) | Con Langfuse |
| :--- | :--- | :--- |
| **Visibilidad de Flujo** | Imprime texto plano en consola (`print()`), perdiendo la relación jerárquica de qué agente llamó a qué subproceso. | **Spans y Traces Jerárquicos:** Árbol de visualización en tiempo real que muestra el tiempo y resultado exacto del Parser Vision, Agente 1 y Agente 2. |
| **Control de Costos y Tokens** | Dificultad para saber cuántos tokens consumió el procesamiento multimodal de las imágenes frente a las llamadas de texto. | **Métricas por Llamada:** Desglose automático de tokens de entrada/salida (incluyendo detalle de tokens de visión) y costo total estimado por contrato. |
| **Depuración de Prompts** | Modificar un prompt requiere buscar en el código y comparar manualmente logs previos. | **Prompt Management & History:** Permite auditoría de los prompts exactos enviados a la API en cada ejecución y su latencia asociada. |
| **Evaluación Continua** | Medir calidad requiere scripts externos aislados. | **Score Ingestion (`create_score`):** El resultado del `Evaluator` (Accuracy) se vincula directamente al Trace en el dashboard de Langfuse. |

#### Ejemplo práctico de superioridad:
En un entorno sin observabilidad, si el Agente 2 falla al estructurar el JSON, es muy difícil determinar si la falla se debió a un mal análisis visual del *Image Parser*, a que el Agente 1 omitió una cláusula en su resumen, o a un error de tipado del Agente 2. Con **Langfuse**, abrimos el *Trace* de la ejecución y podemos inspeccionar el *input/output* exacto de cada Span individualmente en segundos, aislando el error al instante.