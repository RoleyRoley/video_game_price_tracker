# Search steam games by name
# Fetch game's current price

import requests
from typing import List, Dict, Optional

# Steam API endpoints
APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v0002/"
STORE_SEARCH_URL = "https://store.steampowered.com/api/storesearch"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"


class SteamService:
    def __init__(self):
        self.session = requests.Session()
        self.timeout = 10  # seconds

    def get_app_list(self) -> List[Dict]:
        # Fetch the list of all Steam apps.
        response = self.session.get(APP_LIST_URL, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        return data.get("applist", {}).get("apps", [])

    def search_games(self, query: str, limit: int = 10) -> List[Dict]:
        # Search Steam store using the query and return top matches.
        if not query or not query.strip():
            return []

        params = {
            "term": query.strip(),
            "l": "english",
            "cc": "gb"
        }
        
        response = self.session.get(STORE_SEARCH_URL, params=params, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        # Extract relevant info and limit results
        results = []
        for item in items[:limit]:
            if item.get("id") and item.get("name"):
                results.append({
                    "appid": item["id"],
                    "name": item["name"]
                })

        return results

    def get_game_details(self, app_id: int, country_code: str = "gb") -> Optional[Dict]:
        # Fetch game details for a given app id.
        params = {
            "appids": app_id,
            "cc": country_code,
            "l": "english"
        }

        response = self.session.get(APP_DETAILS_URL, params=params, timeout=self.timeout)
        response.raise_for_status()

        
        payload = response.json()
        app_data = payload.get(str(app_id))
        #
        if not app_data or not app_data.get("success"):
            return None

        data = app_data.get("data", {})
        price_overview = data.get("price_overview")
        is_free = data.get("is_free", False)

        # If the game is free, we can return price info with zero values
        if is_free:
            return {
                "steam_app_id": app_id,
                "name": data.get("name"),
                "steam_url": f"https://store.steampowered.com/app/{app_id}/",
                "currency": "GBP",
                "initial_price": 0,
                "final_price": 0,
                "discount_percent": 0,
                "is_free": True
            }

        # If the game is not free, we need price overview data to return meaningful info
        if not price_overview:
            return None

        # Return the relevant details including price info
        return {
            "steam_app_id": app_id,
            "name": data.get("name"),
            "steam_url": f"https://store.steampowered.com/app/{app_id}/",
            "currency": price_overview.get("currency", "GBP"),
            "initial_price": price_overview.get("initial", 0),
            "final_price": price_overview.get("final", 0),
            "discount_percent": price_overview.get("discount_percent", 0),
            "is_free": False
        }