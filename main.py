from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import process_message

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_state: dict

@app.post("/")
async def chat(req: ChatRequest):
    reply, new_state = process_message(req.message, req.conversation_state)
    return {"reply": reply, "conversation_state": new_state}
