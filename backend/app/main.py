from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .api import boq, tender

try:
    from .api import gpt
except ModuleNotFoundError:
    gpt = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"{settings.APP_NAME} v{settings.VERSION} starting...")
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(boq.router, prefix="/api/boq")
if gpt is not None:
    app.include_router(gpt.router, prefix="/api")
app.include_router(tender.router, prefix="/api")

ROOT_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT_DIR / "tender_engine" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/generated", StaticFiles(directory=str(OUTPUT_DIR)), name="generated")


@app.get("/health")
def health():
    return {"status": "healthy", "version": settings.VERSION}
