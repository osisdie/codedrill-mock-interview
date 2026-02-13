from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import problems, sessions, execution, interview, scoring

app = FastAPI(title="CodeDrill", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(problems.router)
app.include_router(sessions.router)
app.include_router(execution.router)
app.include_router(interview.router)
app.include_router(scoring.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
