from curl_cffi import requests
from bs4 import BeautifulSoup
import json
class Match_Crawler: # A specific crawler that is designed to be compatible with whoscored's html.
    def __init__(self, base_url):
        self.base_url = base_url

    def crawl(self): #This returns the
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }

        try:
            response = requests.get(self.base_url,headers = headers, impersonate = "chrome120", timeout = 30)
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.select_one('script:-soup-contains("matchCentreData")')
            raw_text = element.text.split("formationIdNameMappings:")[1].strip() #That is the match centre data in text format. It needs to be converted to json.
            data, _ = json.JSONDecoder().raw_decode(raw_text)
            return data

        except Exception as e:
            print(f"(!) Connection/Parsing error: {e}")
            return None

class League_Crawler(Match_Crawler):
    def __init__(self, league_name, league_season):
        self.name = league_name
        self.season = season
        
