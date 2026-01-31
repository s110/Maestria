import os
import psycopg
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Docker Compose nos permite usar el nombre del servicio como "host"
db_url = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/dbname")

class ResponseModel(BaseModel):
    message: str

@app.get("/", response_model=ResponseModel)
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/health", response_model=ResponseModel)
def health_check():
    try:
        with psycopg.connect(db_url) as conn:
            return {"message": "Connected to Database!"}
    except Exception as e:
        return {"message": f"Database connection failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)