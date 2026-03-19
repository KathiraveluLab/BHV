from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="BHV - Behavioral Health Vault")

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