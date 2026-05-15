from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api import upload, extract, generate, validate, audit, boq, gpt, license
from app.database.session import engine, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("main")

# Create tables if they don't exist (Simple approach for now, Alembic is better for prod migrations)
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")
except Exception as e:
    logger.warning(f"Database connection failed or tables could not be created: {e}")

app = FastAPI(title="Tender Automation", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(extract.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(validate.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(boq.router, prefix="/api/boq")
app.include_router(gpt.router, prefix="/api")
app.include_router(license.router, prefix="/api")

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "tender-automation",
        "database": "connected" # Simplified
    }
