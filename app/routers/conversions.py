import json
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/conversions", tags=["conversions"])

# URL da Calcs API rodando localmente na porta 8000
CALCS_API_URL = "http://127.0.0.1:8000"

# API externa de clima (Open-Meteo) – Rio de Janeiro
WEATHER_API_URL = (
    "https://api.open-meteo.com/v1/forecast?"
    "latitude=-22.90&longitude=-43.20&current=temperature_2m"
)


# -------------------------------
# Função para chamar a Calcs API
# -------------------------------
async def call_calcs_api(calc_type: str, payload: dict) -> dict:
    async with httpx.AsyncClient() as client:

        if calc_type == "three_phase_current":
            endpoint = "/electrical/three_phase_current"
        elif calc_type == "flow_velocity":
            endpoint = "/flow/velocity"
        elif calc_type == "reynolds":
            endpoint = "/flow/reynolds"
        else:
            raise HTTPException(400, "calc_type não suportado")

        url = f"{CALCS_API_URL}{endpoint}"

        response = await client.post(url, json=payload)

        if response.status_code != 200:
            raise HTTPException(
                500, f"Erro ao chamar a Calcs API: {response.text}"
            )

        return response.json()


# -------------------------------
# Função para chamar a Weather API
# -------------------------------
async def get_temperature() -> Optional[float]:
    async with httpx.AsyncClient() as client:
        response = await client.get(WEATHER_API_URL, timeout=5)
        if response.status_code != 200:
            return None

        data = response.json()
        return data.get("current", {}).get("temperature_2m")


# -------------------------------
# CREATE
# -------------------------------
@router.post("", response_model=schemas.ConversionRead)
async def create_conversion(
    body: schemas.ConversionCreate,
    db: Session = get_db(),
):

    # 1) Calcular usando Calcs API
    calc_result = await call_calcs_api(body.calc_type, body.input_payload)

    # 2) Buscar temperatura do clima
    temperature = await get_temperature()

    # 3) Salvar no banco
    db_obj = models.Conversion(
        calc_type=body.calc_type,
        input_payload=json.dumps(body.input_payload),
        result_payload=json.dumps(calc_result),
        temperature_c=temperature,
        description=body.description,
    )

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    return schemas.ConversionRead(
        id=db_obj.id,
        calc_type=db_obj.calc_type,
        input_payload=json.loads(db_obj.input_payload),
        result_payload=json.loads(db_obj.result_payload),
        temperature_c=db_obj.temperature_c,
        description=db_obj.description,
        created_at=db_obj.created_at,
    )


# -------------------------------
# READ ALL
# -------------------------------
@router.get("", response_model=List[schemas.ConversionRead])
def list_conversions(db: Session = get_db()):

    objs = db.query(models.Conversion).order_by(models.Conversion.id.desc()).all()
    result = []

    for obj in objs:
        result.append(
            schemas.ConversionRead(
                id=obj.id,
                calc_type=obj.calc_type,
                input_payload=json.loads(obj.input_payload),
                result_payload=json.loads(obj.result_payload),
                temperature_c=obj.temperature_c,
                description=obj.description,
                created_at=obj.created_at,
            )
        )

    return result


# -------------------------------
# READ ONE
# -------------------------------
@router.get("/{conversion_id}", response_model=schemas.ConversionRead)
def get_conversion(conversion_id: int, db: Session = get_db()):

    obj = db.query(models.Conversion).filter_by(id=conversion_id).first()
    if not obj:
        raise HTTPException(404, "Conversão não encontrada")

    return schemas.ConversionRead(
        id=obj.id,
        calc_type=obj.calc_type,
        input_payload=json.loads(obj.input_payload),
        result_payload=json.loads(obj.result_payload),
        temperature_c=obj.temperature_c,
        description=obj.description,
        created_at=obj.created_at,
    )


# -------------------------------
# UPDATE
# -------------------------------
@router.put("/{conversion_id}", response_model=schemas.ConversionRead)
def update_conversion(
    conversion_id: int,
    body: schemas.ConversionUpdate,
    db: Session = get_db(),
):

    obj = db.query(models.Conversion).filter_by(id=conversion_id).first()
    if not obj:
        raise HTTPException(404, "Conversão não encontrada")

    if body.description is not None:
        obj.description = body.description

    db.commit()
    db.refresh(obj)

    return schemas.ConversionRead(
        id=obj.id,
        calc_type=obj.calc_type,
        input_payload=json.loads(obj.input_payload),
        result_payload=json.loads(obj.result_payload),
        temperature_c=obj.temperature_c,
        description=obj.description,
        created_at=obj.created_at,
    )


# -------------------------------
# DELETE
# -------------------------------
@router.delete("/{conversion_id}")
def delete_conversion(conversion_id: int, db: Session = get_db()):

    obj = db.query(models.Conversion).filter_by(id=conversion_id).first()
    if not obj:
        raise HTTPException(404, "Conversão não encontrada")

    db.delete(obj)
    db.commit()

    return {"detail": "Conversão removida com sucesso"}
