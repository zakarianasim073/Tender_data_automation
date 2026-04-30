import os

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

# Root Files
write_file('README.md', '# 🏗 BOQ AI SaaS\nAI-Powered Bill of Quantities Cost Intelligence Platform\n')
write_file('docker-compose.yml', 'version: "3.9"\nservices:\n  api:\n    build: ./backend\n    ports: ["8000:8000"]\n')
write_file('.gitignore', '__pycache__/\n*.pyc\n*.pyo\n.env\nnode_modules/\ndist/\nbuild/\n.venv/\nvenv/\nuploads/\ncache/\n*.log\n.DS_Store\nThumbs.db\n')

# Backend Files
write_file('backend/requirements.txt', 'fastapi==0.109.0\nuvicorn[standard]==0.27.0\npydantic==2.5.0\npydantic-settings==2.1.0\npyjwt==2.8.0\npython-multipart==0.0.6\nopenai==1.10.0\npandas\nscikit-learn\n')
write_file('backend/app/main.py', 'from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\nfrom app.api import boq, gpt\napp = FastAPI(title="BOQ AI SaaS")\napp.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])\napp.include_router(boq.router, prefix="/api/boq")\napp.include_router(gpt.router, prefix="/api")\n@app.get("/health")\ndef health(): return {"status": "healthy"}\n')
write_file('backend/app/core/config.py', 'from pydantic_settings import BaseSettings\nclass Settings(BaseSettings):\n    APP_NAME: str = "BOQ AI SaaS"\n    JWT_SECRET: str = "secret"\nsettings = Settings()\n')
write_file('backend/app/api/boq.py', 'from fastapi import APIRouter\nrouter = APIRouter()\n@router.post("/diff")\ndef diff(): return {"success": True}\n')
write_file('backend/app/api/gpt.py', 'from fastapi import APIRouter\nrouter = APIRouter(prefix="/gpt")\n@router.post("/chat")\ndef chat(): return {"content": "Hello"}\n')

# Frontend Files
write_file('frontend/package.json', '{"name":"boq-ai","private":true,"version":"1.0.0","type":"module","scripts":{"build":"vite build"},"dependencies":{"react":"^18.2.0","react-dom":"^18.2.0"}}\n')
write_file('frontend/index.html', '<!DOCTYPE html><html><head><title>BOQ AI</title></head><body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body></html>\n')
write_file('frontend/vite.config.js', 'import { defineConfig } from "vite";\nexport default defineConfig({ server: { proxy: { "/api": "https://boq-ai-backend-service.onrender.com" } } });\n')
write_file('frontend/src/main.jsx', 'import React from "react";\nimport ReactDOM from "react-dom/client";\nimport App from "./App";\nReactDOM.createRoot(document.getElementById("root")).render(<App />);\n')
write_file('frontend/src/App.jsx', 'import React from "react";\nexport default function App() { return <h1>BOQ AI Live</h1>; }\n')

# Desktop
write_file('desktop/launcher.py', 'print("BOQ AI Launcher")\n')
write_file('scripts/deploy.sh', 'echo "Deploying..."\n')
