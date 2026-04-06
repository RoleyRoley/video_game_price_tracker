from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.game import Game
from app.services.steam_service import SteamService
from app.services.game_service import recheck_game_price

steam_service = SteamService()
scheduler = BackgroundScheduler()

def auto_recheck_all_games():
    # Fetch all tracked games from the database and recheck their prices.
    db: Session = SessionLocal()
    
    # This function will be scheduled to run periodically to update the prices of all tracked games.
    try:
        games = db.query(Game).all()
        
        for game in db.query(Game).all():
            
            try:
                game_details = steam_service.get_game_details(game.steam_app_id)
                
                
                if game_details:
                    recheck_game_price(db, game.id, game_details)
                    print(f"[Scheduler] Rechecked price for game: {game.name}")
                    
                else:
                    print(f"[Scheduler] Could not fetch details for app ID {game.steam_app_id}")
                
            except Exception as e:
                print(f"[Scheduler] Error re-checking {game.name}: {e}")
    
    finally:
        db.close()
        
def start_scheduler():
    # Start the scheduler to run the auto_recheck_all_games function every 6 hours.
    
    if not scheduler.running:
        # Schedule the job to run every 60 minutes (1 hour).
        scheduler.add_job(
            auto_recheck_all_games,
            trigger="interval", 
            minutes=60,# Run every 60 minutes (1 hour)
            id="auto_recheck_all_games",
            replace_existing=True 
        )
        scheduler.start()
        print("[Scheduler] Started auto price recheck scheduler.")
        
def stop_scheduler():
    # Stop the scheduler if it's running.
    if scheduler.running:
        scheduler.shutdown()
        print("[Scheduler] Stopped auto price recheck scheduler.")