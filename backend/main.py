from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from logger import get_logger
from routers.auth import router as auth_router
from routers.system import router as system_router

logger = get_logger(__name__)

app = FastAPI(
    title="Coverd API",
    version="1.0.0",
    description="Backend API for the Coverd shift management system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    logger.info("Coverd API is starting up")


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Coverd API is shutting down")


@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "service": "coverd-backend"}


app.include_router(system_router)
app.include_router(auth_router)