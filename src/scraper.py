import json
import pandas as pd
from bs4 import BeautifulSoup
from curl_cffi import requests

# --- CONFIGURATION ---
TARGET_URL = "https://www.whoscored.com/matches/1887332/live/international-africa-cup-of-nations-2025-morocco-comoros"
OUTPUT_FILENAME = "afcon_match_events.csv"
# ---------------------

def get_match_data(url):
    """
    Fetches match data using TLS impersonation and robust JSON parsing.
    """
    print(f"--- Fetching data from: {url} ---")
    
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.google.com/"
    }

    try:
        # Use impersonate to bypass TLS fingerprinting
        response = requests.get(url, headers=headers, impersonate="chrome120", timeout=30)
        
        if response.status_code != 200:
            print(f"(!) Failed to fetch page. Status: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.select_one('script:-soup-contains("matchCentreData")')
        
        if not element:
            print("(!) Could not find matchCentreData script tag.")
            return None

        # Isolate the text starting from the opening brace of the JSON
        raw_text = element.text.split("matchCentreData: ")[1].strip()
        
        # --- ROBUST PARSING ---
        # raw_decode parses the first valid JSON object and ignores trailing JS/semicolons.
        data, _ = json.JSONDecoder().raw_decode(raw_text)
        return data

    except Exception as e:
        print(f"(!) Connection/Parsing error: {e}")
        return None

def process_events(matchdict):
    """
    Standardizes and flattens the match events.
    """
    print("--- Processing Events ---")
    df = pd.DataFrame(matchdict['events'])
    
    # Cleaning
    df.dropna(subset='playerId', inplace=True)
    df = df.where(pd.notnull(df), None)
    
    # Renaming for consistency with the uSoccer project
    rename_map = {
        'eventId': 'event_id', 'expandedMinute': 'expanded_minute',
        'outcomeType': 'outcome_type', 'isTouch': 'is_touch',
        'playerId': 'player_id', 'teamId': 'team_id',
        'endX': 'end_x', 'endY': 'end_y',
        'blockedX': 'blocked_x', 'blockedY': 'blocked_y',
        'goalMouthZ': 'goal_mouth_z', 'goalMouthY': 'goal_mouth_y',
        'isShot': 'is_shot', 'cardType': 'card_type', 'isGoal': 'is_goal'
    }
    df = df.rename(columns=rename_map)

    # Map display names from nested dictionaries
    for col in ['period', 'type', 'outcome_type']:
        if col in df.columns:
            df[f'{col}_display_name'] = df[col].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    
    df.drop(columns=["period", "type", "outcome_type"], inplace=True, errors='ignore')

    # Flatten nested qualifiers into columns
    flat_qualifiers = []
    for row in df['qualifiers']:
        row_data = {}
        if isinstance(row, list):
            for item in row:
                name = item.get('type', {}).get('displayName')
                val = item.get('value', True)
                if name:
                    row_data[name] = val
        flat_qualifiers.append(row_data)

    qual_df = pd.DataFrame(flat_qualifiers, index=df.index)
    df = pd.concat([df.drop(columns=['qualifiers'], errors='ignore'), qual_df], axis=1)

    # Convert numeric columns to appropriate types
    for col in qual_df.columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            continue

    return df

if __name__ == "__main__":
    match_data = get_match_data(TARGET_URL)
    
    if match_data:
        events_df = process_events(match_data)
        events_df.to_csv(OUTPUT_FILENAME, index=False)
        print(f"--- SUCCESS --- Data saved to {OUTPUT_FILENAME}")
        print(f"Total events processed: {len(events_df)}")
    else:
        print("Scraping failed.")