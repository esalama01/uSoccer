import os
import json
from pathlib import Path

def extract_global_mappings():
    # 1. Define paths based on your repository architecture
    initial_dir = r"../../scraper/data"
    output_path = Path("../data/global_mappings.json")
    
    # Initialize global dictionaries
    global_players = {}
    global_teams = {}
    
    # 2. Load existing data if file exists to perform an incremental merge
    if output_path.exists():
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
                global_players = existing_data.get("players", {})
                global_teams = existing_data.get("teams", {})
            print(f"Loaded existing reference maps: {len(global_players)} players, {len(global_teams)} teams.")
        except Exception as e:
            print(f"Could not load existing file (starting fresh): {e}")

    processed_count = 0
    failed_count = 0

    if not os.path.exists(initial_dir):
        print(f"Error: Target tracking root directory '{initial_dir}' does not exist.")
        return

    print("Beginning directory traversal for metadata extraction...")
    
    # 3. Traverse identical folder structure: initial_dir -> league -> season -> files
    with os.scandir(initial_dir) as leagues:
        for league in leagues:
            if league.is_dir():
                with os.scandir(league.path) as seasons:
                    for season in seasons:
                        if season.is_dir():
                            with os.scandir(season.path) as match_files:
                                for file in match_files:
                                    # Ensure we are parsing raw source JSON files
                                    if file.is_file() and file.name.endswith(".json"):
                                        try:
                                            with open(file.path, "r", encoding="utf-8") as f:
                                                game_data = json.load(f)
                                            
                                            # Extract Player Dictionary
                                            match_players = game_data.get("playerIdNameDictionary", {})
                                            global_players.update(match_players)
                                            
                                            # Extract Teams (Home & Away structures)
                                            for side in ["home", "away"]:
                                                team_info = game_data.get(side, {})
                                                t_id = team_info.get("teamId")
                                                t_name = team_info.get("name")
                                                if t_id and t_name:
                                                    global_teams[str(t_id)] = t_name
                                            
                                            processed_count += 1
                                            if processed_count % 500 == 0:
                                                print(f"Processed {processed_count} match files...")
                                                
                                        except Exception as e:
                                            failed_count += 1
                                            continue 

    # 4. Save consolidated state safely back to disk
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    payload = {
        "players": global_players,
        "teams": global_teams
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)
        
    print("\n" + "="*40)
    print("MAPPING EXTRACTION COMPLETE")
    print("="*40)
    print(f"Successfully Parsed Match Files: {processed_count}")
    print(f"Failed/Skipped Files:           {failed_count}")
    print(f"Total Unique Players Cached:     {len(global_players)}")
    print(f"Total Unique Teams Cached:       {len(global_teams)}")
    print(f"Saved reference file to:        {output_path.resolve()}")

if __name__ == "__main__":
    extract_global_mappings()