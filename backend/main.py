from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agent import run_agent, start_practice

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def index():
    return FileResponse("frontend/index.html")

@app.post("/chat")
def chat(request: ChatRequest):
    return run_agent(request.message)

@app.post("/start_practice")
def practice():
    return start_practice()
