from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


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

templates = Jinja2Templates(directory="app/templates")


app.include_router(games_router)

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request}
    )





