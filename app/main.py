from fastapi import FastAPI
from .routers import router

app = FastAPI(title="Auth Service")

app.include_router(router)