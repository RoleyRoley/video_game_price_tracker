from app.models.price_history import PriceHistory

def get_latest_two_prices(db, game_id: int):
    return (
        db.query(PriceHistory)
        .filter(PriceHistory.game_id == game_id)
        .order_by(PriceHistory.checked_at.desc())
        .limit(2)
        .all()
    )

def calculate_price_change(previous_price: int, current_price: int):

    # Calculate the price difference and percentage change.
    difference = current_price - previous_price

    if previous_price == 0:
        percentage_change = 0
    else:
        # Calculate the percentage change and round it to 2 decimal places.
        percentage_change = round((difference / previous_price) * 100, 2)

    # Return the price difference and percentage change as a dictionary.
    return {
        "difference": difference,
        "percentage_change": percentage_change
    }
