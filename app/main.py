from fastapi import FastAPI
from app.db import Base, engine
from app.routers import health, conversions

# cria as tabelas (jeito simples, sem Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EngLab Orchestrator API",
    description="API principal que orquestra cálculos e clima",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "EngLab Orchestrator API - OK"}


app.include_router(health.router)
app.include_router(conversions.router)
