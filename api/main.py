from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from middleware.error_handler import register_error_handlers

app = FastAPI(
    title="RepoMind API",
    description=(
        "The ML core of HackingTheRepo. "
        "Receives a natural-language instruction and a repo URL, "
        "clones the repo, plans and applies code changes, and opens a Pull Request automatically."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(router)

@app.get("/", tags=["Health"])
async def root():
    return {"service": "RepoMind", "status": "running"}

@app.get("/health", tags=["Health"])
async def health():
    from core.job_manager import job_manager
    return {"status": "ok", "jobs": job_manager.stats()}
