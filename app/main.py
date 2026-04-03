from fastapi import FastAPI
from .routers import router

app = FastAPI(title="Service d'authentification")

app.include_router(router)