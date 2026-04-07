from app.services.loaded_service import LoadedService

loaded = LoadedService()

url = "https://www.loaded.com/elden-ring-pc-steam"
details = loaded.get_game_details(url)

print(details)