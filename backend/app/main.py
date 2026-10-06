import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.db import init_db
from app.api.routes import router

logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("ai_research_analyst")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SQLite database tables...")
    init_db()
    logger.info(f"AI Research Analyst API online. Model: {settings.OPENAI_MODEL}, Search: {settings.SEARCH_PROVIDER}")
    yield
    logger.info("Shutting down AI Research Analyst API...")

app = FastAPI(
    title="AI Research Analyst API",
    description="Production-style agentic AI research system featuring question decomposition, bounded tool calling, evidence mining, conflict arbitration, source verification, and structured report synthesis.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "service": "AI Research Analyst API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }
