# main.py

from fastapi import FastAPI
from rotas import gc


app = FastAPI()

app.include_router(gc.router)
