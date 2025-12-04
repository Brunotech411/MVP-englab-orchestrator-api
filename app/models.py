from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.db import Base


class Conversion(Base):
    __tablename__ = "conversions"

    id = Column(Integer, primary_key=True, index=True)
    # tipo de cálculo, ex: "three_phase_current" ou "flow_velocity"
    calc_type = Column(String, index=True)
    # parâmetros de entrada em texto (JSON serializado)
    input_payload = Column(String)
    # resultado do cálculo em texto (JSON serializado)
    result_payload = Column(String)
    # temperatura retornada pela API de clima
    temperature_c = Column(Float, nullable=True)
    # por exemplo: "dimensionamento cabo bomba P-2103"
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
