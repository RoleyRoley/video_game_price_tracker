from fastapi import FastAPI
from pydantic import BaseModel


from app.db.database import engine
from app.routes.games import router as games_router

# TESTING
try:
    connection = engine.connect()
    print("Database connection successful!")
    connection.close()
except Exception as e:
    print(f"Database connection failed: {e}")




app = FastAPI(title="Game Price Tracker")

app.include_router(games_router)

@app.get("/")
def root():
    return {"message": "Game Price Tracker API is running"}





