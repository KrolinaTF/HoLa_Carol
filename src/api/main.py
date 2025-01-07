from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .middleware.auth import AuthMiddleware
from .routes import medical_routes, botanical_routes, chemical_routes, biological_routes, physical_routes
import logging
from src.utils.logger import setup_logger
from src.orchestrator.orchestrator import Orchestrator
from dotenv import load_dotenv
import os

load_dotenv()

# Variables de entorno
API_VERSION = os.getenv("API_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configuración del logger
logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta al iniciar
    logger.info("API starting up...")
    from src.utils.database import init_db
    init_db()
    
    # Inicializar Orchestrator como variable global
    global orchestrator
    orchestrator = Orchestrator()
    
    yield
    
    # Código que se ejecuta al cerrar
    logger.info("API shutting down...")

app = FastAPI(
    title="Medical Expert System API",
    description="API for medical consultations with holistic approach",
    version="1.0.0",
    docs_url=None if ENVIRONMENT == "production" else "/docs",
    redoc_url=None if ENVIRONMENT == "production" else "/redoc",
    lifespan=lifespan
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Añadir middleware de autenticación
app.add_middleware(AuthMiddleware)

# Incluir rutas
app.include_router(medical_routes.router)
app.include_router(botanical_routes.router)
app.include_router(chemical_routes.router)
app.include_router(biological_routes.router)
app.include_router(physical_routes.router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error occurred: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}