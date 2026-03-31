# TESTING

from app.services.steam_service import SteamService

steam = SteamService()

results = steam.search_games("elden ring", limit=5)
print("SEARCH RESULTS:")
for game in results:
    print(game)
    
if results:
    app_id = results[0]["appid"]
    details = steam.get_game_details(app_id)
    print("\nGAME DETAILS:")
    print(details)