import os
import json
from pathlib import Path

def extract_global_mappings():
    # Force absolute paths to eliminate relative path ambiguity
    initial_dir = Path("/home/esalama01/projects/uSoccer/scraper/data")
    output_path = Path("/home/esalama01/projects/uSoccer/data/global_mappings.json")
    
    global_players = {}
    global_teams = {}
    
    # Create target directory if it doesn't exist yet
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing data if it's a re-run
    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                global_players = existing_data.get("players", {})
                global_teams = existing_data.get("teams", {})
            print(f"Loaded existing maps: {len(global_players)} players, {len(global_teams)} teams.")
        except Exception as e:
            print(f"Could not load existing file (starting fresh): {e}")

    if not initial_dir.exists():
        print(f"Error: Raw scraper directory not found at {initial_dir.resolve()}")
        return

    print(f"Scanning raw files in {initial_dir.resolve()}...")
    processed_count = 0

    # Traverse absolute path: scraper/data -> league -> season -> *.json
    for league_dir in initial_dir.iterdir():
        if league_dir.is_dir():
            for season_dir in league_dir.iterdir():
                if season_dir.is_dir():
                    for file_path in season_dir.glob("*.json"):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                game_data = json.load(f)
                            
                            # Grab players
                            match_players = game_data.get("playerIdNameDictionary", {})
                            global_players.update(match_players)
                            
                            # Grab teams
                            for side in ["home", "away"]:
                                team_info = game_data.get(side, {})
                                t_id = team_info.get("teamId")
                                t_name = team_info.get("name")
                                if t_id and t_name:
                                    global_teams[str(t_id)] = t_name
                            
                            processed_count += 1
                        except Exception:
                            continue

    # Save consolidated map state back to disk
    payload = {
        "players": global_players,
        "teams": global_teams
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)
        
    print("\n" + "="*40)
    print("MAPPING EXTRACTION COMPLETE")
    print("="*40)
    print(f"Processed Files:        {processed_count}")
    print(f"Unique Players Cached:  {len(global_players)}")
    print(f"Unique Teams Cached:    {len(global_teams)}")
    print(f"Saved absolutely to:    {output_path.resolve()}")

if __name__ == "__main__":
    extract_global_mappings()