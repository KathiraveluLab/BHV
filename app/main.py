from fastapi import FastAPI

app = FastAPI(title="BHV - Behavioral Health Vault")

@app.get("/")
def root():
    return {"message": "BHV API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}