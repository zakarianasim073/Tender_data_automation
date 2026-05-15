from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import upload, extract, generate, validate, audit, boq, gpt, license

app = FastAPI(title="Tender Automation", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

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
    return {"status": "healthy", "service": "tender-automation"}
