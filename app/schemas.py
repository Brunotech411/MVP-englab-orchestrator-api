from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, Field


class ConversionCreate(BaseModel):
    calc_type: str = Field(..., description="Tipo de cálculo, ex: three_phase_current")
    # Aqui vamos aceitar qualquer payload de entrada (dict)
    input_payload: dict
    description: Optional[str] = None


class ConversionUpdate(BaseModel):
    description: Optional[str] = None


class ConversionRead(BaseModel):
    id: int
    calc_type: str
    input_payload: dict
    result_payload: dict
    temperature_c: Optional[float]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # para usar com SQLAlchemy
