from fastapi import APIRouter, HTTPException, Depends, Request, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.game import Game
from app.models.price_history import PriceHistory

# Import services
from app.services.steam_service import SteamService
from app.services.game_service import save_game_and_price, get_game_by_id, recheck_game_price
from app.services.price_service import get_latest_two_prices, calculate_price_change
from app.services.loaded_service import LoadedService


# Initialize the API router and Steam service
router = APIRouter()
steam_service = SteamService()
loaded_service = LoadedService()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    # Dependency to get a database session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.get("/search")
def search_games(query: str):
    # Search Steam for game matching query.
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter cannto be empty.")
    
    results = steam_service.search_games(query)
    
    # Return the search results as JSON
    return {
        "query": query,
        "results": results
    }


@router.post("/search-page")
def search_games_page(request: Request, query: str = Form(...)):
    if not query or not query.strip():
        return templates.TemplateResponse(
            request=request,
            name="search_results.html",
            context={"request": request, "query": query, "results": []}
        )

    results = steam_service.search_games(query=query.strip(), limit=10)
    return templates.TemplateResponse(
        request=request,
        name="search_results.html",
        context={"request": request, "query": query, "results": results}
    )
    
@router.post("/track")
def track_game(steam_app_id: int, db: Session = Depends(get_db)):
    # Track a game by its Steam app ID.
    
    game_details = steam_service.get_game_details(steam_app_id)

    # If game details could not be fetched, return an error response.    
    if not game_details:
        raise HTTPException(status_code=404, detail="Game not found on Steam.")
        
    game, price_record = save_game_and_price(db, game_details)
    
    return {
        "message": "Game tracked successfully.",
        "game": {
            "id": game.id,
            "steam_app_id": game.steam_app_id,
            "name": game.name,
            "steam_url": game.steam_url
        },
        "price_record": {
            "id": price_record.id,
            "initial_price": price_record.initial_price,
            "final_price": price_record.final_price,
            "discount_percent": price_record.discount_percent,
            "currency": price_record.currency,
            "checked_at": price_record.checked_at
            
        }
    }


@router.post("/track-page")
def track_game_page(steam_app_id: int = Form(...), db: Session = Depends(get_db)):
    game_details = steam_service.get_game_details(steam_app_id)
    if not game_details:
        raise HTTPException(status_code=404, detail="Game not found on Steam.")

    save_game_and_price(db, game_details)
    return RedirectResponse(url="/tracked-games-page", status_code=status.HTTP_303_SEE_OTHER)
    
@router.get("/tracked-games")
# Retrieve all tracked games with their latest price info.
def get_tracked_games(db: Session = Depends(get_db)):
    # Retrieve all tracked games with their latest price info.
    
    games = db.query(Game).all()
    tracked_games = []
    
    
    for game in games:
        latest_price = (
            db.query(PriceHistory)
            .filter(PriceHistory.game_id == game.id)
            .order_by(PriceHistory.checked_at.desc())
            .first()
        )
        # Append game info along with its latest price data to the tracked_games list.
        tracked_games.append({
            "id": game.id,
            "steam_app_id": game.steam_app_id,
            "name": game.name,
            "steam_url": game.steam_url,
            "latest_price": {
                "initial_price": latest_price.initial_price if latest_price else None,
                "final_price": latest_price.final_price if latest_price else None,
                "discount_percent": latest_price.discount_percent if latest_price else None,
                "currency": latest_price.currency if latest_price else None,
                "checked_at": latest_price.checked_at if latest_price else None,
            }
        })
    
    # Return the list of tracked games with their latest price info.
    return {
        "count": len(tracked_games),
        "tracked_games": tracked_games
    }


@router.get("/tracked-games-page")
def get_tracked_games_page(request: Request, db: Session = Depends(get_db)):
    games = db.query(Game).all()

    tracked_games = []

    for game in games:
        latest_prices = get_latest_two_prices(db, game.id)

        latest_price = latest_prices[0] if len(latest_prices) > 0 else None
        previous_price = latest_prices[1] if len(latest_prices) > 1 else None

        price_change = None
        if latest_price and previous_price:
            price_change = calculate_price_change(
                previous_price.final_price,
                latest_price.final_price
            )

        # 🔥 NEW: Try Loaded lookup
        loaded_price = None

        try:
            # simple approach: search by name (you can refine later)
            search_results = loaded_service.search_games(game.name)

            if search_results:
                first_result = search_results[0]
                loaded_details = loaded_service.get_game_details(first_result["url"])
                loaded_price = loaded_details

        except Exception as e:
            print(f"[Loaded] Error fetching price for {game.name}: {e}")

        tracked_games.append({
            "id": game.id,
            "steam_app_id": game.steam_app_id,
            "name": game.name,
            "steam_url": game.steam_url,
            "latest_price": latest_price,
            "previous_price": previous_price,
            "price_change": price_change,
            "loaded_price": loaded_price
        })

    return templates.TemplateResponse(
        request=request,
        name="tracked_games.html",
        context={"tracked_games": tracked_games}
    )

@router.post("/recheck-price/{game_id}")
@router.post("/recheck/{game_id}")
def recheck_game(game_id: int, db: Session = Depends(get_db)):
    
    game = get_game_by_id(db, game_id)
    
    # If the game is not found in the database, return a 404 error response.
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # Fetch the latest game details from Steam using the game's Steam app ID.
    game_details = steam_service.get_game_details(game.steam_app_id)

    # If the game details could not be fetched from Steam, return a 404 error response.
    if not game_details:
        raise HTTPException(status_code=404, detail="Could not fetch latest Steam data")

    # Update the game's price information in the database and create a new price history record.
    recheck_game_price(db, game_id, game_details)

    return RedirectResponse(url="/tracked-games-page", status_code=303)