from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Coverd API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}
