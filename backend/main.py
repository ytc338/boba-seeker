from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import shops, brands
from app.database import engine, Base

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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(shops.router, prefix="/api/shops", tags=["shops"])
app.include_router(brands.router, prefix="/api/brands", tags=["brands"])


@app.get("/")
def root():
    return {"message": "Welcome to Boba Seeker API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
