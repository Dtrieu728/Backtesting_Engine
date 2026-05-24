from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.backTestAPI import router
from db.database import init_db
from contextlib import asynccontextmanager

app = FastAPI(title="Backtesting Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://backtesting-engine-mklub5j0d-dustine-trieus-projects.vercel.app/",
                   "https://backtesting-engine.vercel.app",],  # React dev server,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    
app = FastAPI(title="Backtesting Engine", lifespan=lifespan)
app.include_router(router, prefix="/api")