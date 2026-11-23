from pathlib import Path
import vdf

steamapps = Path(r"C:\Program Files (x86)\Steam\steamapps")


for path in steamapps.glob("appmanifest_*.acf"):
    with path.open(encoding="utf-8") as file:
        data = vdf.load(file)
        
    app = data["AppState"]
    print(app["appid"], app["name"])