from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.backTestAPI import router

app = FastAPI(title="Backtesting Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")