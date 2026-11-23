import json
from pathlib import Path


games_path = Path(__file__).with_name("owned_games.json")

if not games_path.exists():
    raise SystemExit(f"Couldn't find {games_path.name}. Run scan_owned.py first.")

games = json.loads(games_path.read_text(encoding="utf-8"))

known_owners = sorted({
    owner
    for game in games
    for owner in game.get("owners", [])
})

print("Known owners:", ", ".join(known_owners))
entered_names = input("Enter at least two names, separated by commas: ")

# Match names without regard to capitalization, while keeping their saved spelling.
owners_by_lowercase = {owner.casefold(): owner for owner in known_owners}
selected_owners = []
unknown_names = []

for entered_name in entered_names.split(","):
    name = entered_name.strip()
    if not name:
        continue

    saved_name = owners_by_lowercase.get(name.casefold())
    if saved_name is None:
        unknown_names.append(name)
    elif saved_name not in selected_owners:
        selected_owners.append(saved_name)

if unknown_names:
    raise SystemExit(f"Unknown owner name(s): {', '.join(unknown_names)}")

if len(selected_owners) < 2:
    raise SystemExit("Please enter at least two different known names.")

common_games = [
    game
    for game in games
    if all(owner in game.get("owners", []) for owner in selected_owners)
    and game.get("tags")
]
common_games.sort(key=lambda game: game.get("name", "").casefold())

print(f"\nGames owned by all of {', '.join(selected_owners)}:")
if common_games:
    for game in common_games:
        tags = game.get("tags", [])
        tag_text = f" ({', '.join(tags)})" if tags else ""
        print(f"- {game.get('name', 'Unknown game')}{tag_text}")
else:
    print("No games found in common.")

print(f"\n{len(common_games)} common game(s).")
