import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import shops, brands, feedback
from app.database import engine, Base
from app.logger import logger
import time
from fastapi import Request

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Boba Seeker API",
    description="API for discovering boba tea shops in Taiwan and the US",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        os.environ.get("FRONTEND_URL", ""),  # Render frontend URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.2f}ms"
    )
    return response


@app.on_event("startup")
async def startup_event():
    logger.info("Boba Seeker API starting up...")

# Include routers
app.include_router(shops.router, prefix="/api/shops", tags=["shops"])
app.include_router(brands.router, prefix="/api/brands", tags=["brands"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])


@app.get("/")
def root():
    return {"message": "Welcome to Boba Seeker API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
