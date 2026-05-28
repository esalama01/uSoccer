from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import re
import json5

class MatchScraper: # A specific crawler that is designed to be compatible with whoscored's html.
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
            element = soup.select_one('script:-soup-contains("var allRegions")')
            txt = element.text
            raw_text = txt.split("var allRegion:")
            data, _ = json.JSONDecoder().raw_decode(raw_text) #Got it converted to json format
            return data #data in json format

        except Exception as e:
            print(f"(!) Connection/Parsing error: {e}")
            return None

class LeagueScraper(MatchScraper):
    def __init__(self, league_name, league_season, country = None): #league season must be in (xxxx-yyyy) format
        #It's much better if the league country was provided.
        season_pattern = r"^(\d{4})-\d{4}$"
        name_pattern = r""
        if not re.fullmatch(season_pattern, league_season):
            raise ValueError("season must be in (xxxx-yyyy) format.")
        #If league_name not in leagues, i must call get_league on it.

        self.name = league_name
        self.season = league_season
        self.country = country

    def all_leagues(self):#Scrape whoscored.com
        url = "https://www.whoscored.com"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }
        try:
            response = requests.get(url,headers = headers, impersonate = "chrome120", timeout = 30)
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.select_one('script:-soup-contains("matchCentreData ")')
            raw_text = element.text.split("var allRegion= ")[0].strip().replace("var allRegions = ","")
            txtt = raw_text.split(",\n")
            new_list = []
            for element in txtt:
                new_list.append(json5.loads(element))
            return element
        except Exception as e:
            print(f"(!) Connection/Parsing error: {e}")
            return None

    def get_league(self):  # scrapes whoscored.com -> Gets the leagues ids and names and urls out of it -> For each league it gets the years and the stage ids out of it and saves all of this in a json file named dict.json
        leagues = self.all_leagues()
        if self.country != None:
            for element in leagues:
                if element['name'].lower() == self.country.lower():
                    for tournament in element['tournaments']:
                        if tournament['name'].lower() == self.name.lower():
                            url = tournament['url']
                            break
                    break




