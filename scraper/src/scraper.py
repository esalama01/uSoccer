import json
import pandas as pd
from bs4 import BeautifulSoup
from curl_cffi import requests

# --- CONFIGURATION ---
TARGET_URL = "https://www.whoscored.com/matches/1914240/live/spain-laliga-2025-2026-espanyol-real-madrid"
OUTPUT_FILENAME = "new.csv"
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


if __name__ == "__main__":
    match_data = get_match_data(TARGET_URL)
    
    if match_data:
        events_df = df = pd.DataFrame(match_data['events'])
        events_df.to_csv(OUTPUT_FILENAME, index=False)
        print(f"--- SUCCESS --- Data saved to {OUTPUT_FILENAME}")
        print(f"Total events processed: {len(events_df)}")
    else:
        print("Scraping failed.")