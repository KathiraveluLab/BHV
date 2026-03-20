from fastapi import FastAPI
from pydantic import BaseModel
from app.database.db import Base, engine
from app.routes import auth

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BHV - Behavioral Health Vault",
    description="A secure platform for behavioral health data management",
    version="0.1.0"
)

# Include routers
app.include_router(auth.router)

class RootResponse(BaseModel):
    message: str

class HealthResponse(BaseModel):
    status: str

@app.get("/", response_model=RootResponse)
def root() -> RootResponse:
    """Root endpoint to check if the API is running."""
    return RootResponse(message="BHV API is running")

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check endpoint to verify service is up."""
    return HealthResponse(status="healthy")