from fastapi import FastAPI, HTTPException
from database import supabase

app = FastAPI(
    title="FastAPI + Supabase Backend",
    description="Backend with Supabase client",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "FastAPI + Supabase backend running 🚀"}
