from enum import Enum
from pydantic import BaseModel
from fastapi import FastAPI


class SessionStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"


class SessionState(BaseModel):
    status: SessionStatus = SessionStatus.IDLE
    supervised: bool = True
    emergency_stop_enabled: bool = True
    real_input_control_enabled: bool = False


app = FastAPI(
    title="lain-desk-agent",
    description="A supervised local desktop agent prototype.",
    version="0.1.0",
)

state = SessionState()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/session", response_model=SessionState)
def get_session() -> SessionState:
    return state


@app.post("/session/start", response_model=SessionState)
def start_session() -> SessionState:
    state.status = SessionStatus.RUNNING
    return state


@app.post("/session/stop", response_model=SessionState)
def stop_session() -> SessionState:
    state.status = SessionStatus.IDLE
    return state
