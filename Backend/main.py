from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.backTestAPI import router
from db.database import init_db

app = FastAPI(title="Backtesting Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://backtesting-engine-mklub5j0d-dustine-trieus-projects.vercel.app/",],  # React dev server,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()

app.include_router(router, prefix="/api")