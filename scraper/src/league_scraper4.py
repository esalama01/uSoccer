import json
import os
import time
import re
from bs4 import BeautifulSoup
from curl_cffi import requests

# --- CONFIGURATION ---
STAGE_ID = "21149"  # 
# Spanish La Liga typically runs from August to May
MONTHS_TO_SCRAPE = [
     "202208", "202209", "202210", "202211", "202212", 
    "202301", "202302", "202303", "202304", "202305"
]
OUTPUT_DIR = "../data/Liga Portugal/portugal-liga-2022-2023"
# ---------------------

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.google.com/"
}

def get_league_schedule(stage_id, year_month):
    """
    Fetches all match IDs for a specific month in the league schedule.
    """
    url = f"https://www.whoscored.com/tournaments/{stage_id}/data/?d={year_month}"
    print(f"--- Fetching schedule for {year_month} ---")
    
    try:
        response = requests.get(url, headers=HEADERS, impersonate="chrome120", timeout=30)
        
        if response.status_code != 200:
            print(f"(!) Failed to fetch schedule. Status: {response.status_code}")
            return []

        data = response.json()
        match_ids = []
        
        # Parse the JSON response to extract match IDs
        for tourney in data.get('tournaments', []):
            for match in tourney.get('matches', []):
                match_ids.append(match['id'])
                
        return match_ids
    except Exception as e:
        print(f"(!) Error fetching schedule: {e}")
        return []

def get_match_data(match_id):
    """
    Fetches match data using TLS impersonation and robust JSON parsing.
    """
    url = f"https://www.whoscored.com/Matches/{match_id}/Live"
    print(f"Fetching data for match {match_id}...")
    
    try:
        response = requests.get(url, headers=HEADERS, impersonate="chrome120", timeout=30)
        
        if response.status_code != 200:
            print(f"(!) Failed to fetch page. Status: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.select_one('script:-soup-contains("matchCentreData")')
        
        if not element:
            print("(!) Could not find matchCentreData script tag. (Game might not have started yet)")
            return None

        raw_text = element.text.split("matchCentreData: ")[1].strip()
        data, _ = json.JSONDecoder().raw_decode(raw_text)
        return data
    except Exception as e:
        print(f"(!) Connection/Parsing error: {e}")
        return None

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    all_match_ids = []
    
    # 1. Collect all match IDs for the season
    print("Gathering season schedule...")
    for month in MONTHS_TO_SCRAPE:
        ids = get_league_schedule(STAGE_ID, month)
        all_match_ids.extend(ids)
        time.sleep(1)  # Be polite to the API
        
    print(f"\nFound {len(all_match_ids)} total matches to scrape.")
    
    # 2. Iterate through matches and scrape them
    for i, match_id in enumerate(all_match_ids, 1):
        filename = os.path.join(OUTPUT_DIR, f"{match_id}_match_data.json")
        
        # Check if file already exists to allow for safe pausing/resuming
        if os.path.exists(filename):
            print(f"[{i}/{len(all_match_ids)}] Match {match_id} already exists. Skipping.")
            continue
            
        print(f"\n[{i}/{len(all_match_ids)}] Processing...")
        match_data = get_match_data(match_id)
        
        if match_data:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(match_data, f, ensure_ascii=False, indent=4)
            print(f"--- SUCCESS --- Saved to {filename}")
        else:
            print(f"--- SKIPPED --- Match {match_id} failed or has no data yet.")
            
        # CRITICAL: Wait between 3 to 5 seconds between matches to avoid IP bans

    print("\n--- SCRAPING COMPLETE ---")