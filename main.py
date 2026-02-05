from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import logging
import sys

from config import SECRET_KEY
from db import init_db

from app.routers.auth import router as auth_router
from app.routers.gallery import router as gallery_router
from app.routers.pages import router as pages_router
from app.routers.narrative import router as narrative_router

logger = logging.getLogger("bhv")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)

app = FastAPI(title="BHV Platform", version="0.1.0")

init_db()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages_router)
app.include_router(auth_router)
app.include_router(gallery_router)
app.include_router(narrative_router)


@app.on_event("startup")
async def on_startup():
    logger.info("Starting BHV Platform application")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down BHV Platform application")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

