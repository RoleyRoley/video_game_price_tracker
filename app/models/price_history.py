from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from datetime import datetime, timezone
from app.db.database import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    
    # Link to game
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    
    # Price data
    initial_price = Column(Integer) # Original price before discount
    final_price = Column(Integer) # Price after discount
    discount_percent = Column(Integer) # Discount percentage
    
    # Currency code (e.g., "GBP", "USD")
    currency = Column(String, default="GBP")
    
    # When the price was recorded
    checked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)) 