from fastapi import FastAPI, HTTPException
from database import supabase
from fastapi.middleware.cors import CORSMiddleware
from api.user import router as user_router
from api.login import router as login_router

app = FastAPI(
    title="FastAPI + Supabase Backend",
    description="Backend with Supabase client",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(login_router)


@app.get("/")
def root():
    return {"message": "FastAPI + Supabase backend running 🚀"}
