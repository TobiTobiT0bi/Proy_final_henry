from typing import List
from pydantic import BaseModel, Field

class ContractChangeOutput(BaseModel):
    """Modelo estructurado para representar los cambios entre un contrato y su enmienda."""

    sections_changed: List[str] = Field(
        ..., 
        description="Nombres de las secciones o cláusulas modificadas"
    )
    topics_touched: List[str] = Field(
        ...,
        description="Categorías legales o comerciales afectadas (ej: 'Monto', 'Vigencia', 'Confidencialidad')"
    )
    summary_of_the_change: str = Field(
        ...,
        description="Descripción detallada, concisa y precisa de los cambios identificados"
    )