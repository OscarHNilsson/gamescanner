import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ["STEAM_API_KEY"]
steam_id = os.environ["DONCE"]
cache_path = Path(__file__).with_name("steam_cache.json")

if cache_path.exists():
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
else:
    cache = {}
    
    
def get_categories(appid):
    appid = str(appid)
    
    if appid in cache:
        print(f"Using cached categories for app: {appid}")
        return cache[appid]

    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    
    try:
        request = Request(
            url,
            headers={
                "User-Agent": "GameScanner/1.0",
                "Accept": "application/json",
            },
        )

        with urlopen(request, timeout=20) as response:
            result = json.load(response)[appid]
            
        if not result.get("success"):
            return []
        
        categories = result["data"].get("categories", [])
        descriptions = [category["description"] for category in categories]
        cache[appid] = descriptions
        print(f"Fetched categories for app: {appid}")
        cache_path.write_text(
            json.dumps(cache, indent=2),
            encoding="utf-8",       
        )
        
        time.sleep(3)
        return descriptions
    
    except HTTPError as error:
        print(f"Steam refused app {appid}: HTTP {error.code}")
        print(error.read().decode("utf-8", errors="replace")[:500])
        return []
    
    except (KeyError, TimeoutError, OSError, json.JSONDecodeError) as error:
        print(f"Could not check app {appid}: {error}")
        return []

params = urlencode({
    "key": api_key,
    "steamid": steam_id,
    "include_appinfo": 1
})

url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?{params}"

with urlopen(url) as response:
    data = json.load(response)
    
games = data["response"].get("games", [])

multiplayer_labels = {
    "Multi-player",
    "Online PvP",
    "LAN PvP",
    "Shared/Split Screen PvP",
    "Co-op",
    "Online Co-op",
    "LAN Co-op",
    "Shared/Split Screen Co-op",
}

for game in games:
    categories = get_categories(game["appid"])
    multiplayer = multiplayer_labels.intersection(categories)
    
    if multiplayer:
        print(f'{game.get("name", "Unknown game")}: {", ".join(sorted(multiplayer))}')
    
print(f"Found {len(games)} games")