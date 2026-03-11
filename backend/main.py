from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from backend.agent import run_agent, start_practice

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = ROOT_DIR

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.post("/chat")
def chat(request: ChatRequest):
    return run_agent(request.message)

@app.post("/start_practice")
def practice():
    return start_practice()
