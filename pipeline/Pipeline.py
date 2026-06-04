from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import re
import json5
import tempfile
import pandas as pd
from socceraction.data.opta.parsers import WhoScoredParser
from socceraction.spadl.opta import convert_to_actions
from socceraction.data.opta.loader import _eventtypesdf
from socceraction.spadl import config as spadlconfig
import socceraction.vaep.features as fs
import socceraction.vaep.labels as lab
#import time

class MatchScraper: # A specific crawler that is designed to be compatible with whoscored's html.
    def __init__(self, base_urls):
        self.base_urls = base_urls

    def crawl(self): #This returns the match event data in json format
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }
        all_match_data = []
        for base_url in self.base_urls:
            try:
                response = requests.get(base_url,headers = headers, impersonate = "chrome120", timeout = 30)
                soup = BeautifulSoup(response.text, 'html.parser')
                element = soup.select_one('script:-soup-contains("matchCentreData")')
                if not element:
                    print("(!) Could not find matchCentreData script tag. (Game might not have started yet)")
                    continue

                raw_text = element.text.split("matchCentreData: ")[1].strip()
                data, _ = json.JSONDecoder().raw_decode(raw_text) #Got it converted to json format
                all_match_data.append({'data':data, 'url':base_url}) #data in json format

            except Exception as e:
                print(f"(!) Connection/Parsing error: {e}")
                continue
        return all_match_data

class LeagueScraper(MatchScraper):
    def __init__(self, league_name, league_season, country = None): #league season must be in (xxxx/yyyy) format
        #It's much better if the league country was provided.
        season_pattern = r"^(\d{4})/\d{4}$"
        name_pattern = r""
        if not re.fullmatch(season_pattern, league_season):
            raise ValueError("season must be in (xxxx/yyyy) format.")
        #If league_name not in leagues, i must call get_league on it.

        self.name = league_name
        self.season = league_season
        self.country = country
        self.session = requests.Session(impersonate="chrome120")
        super().__init__(base_urls=[])

    def all_leagues(self):#Scrape whoscored.com
        new_list = []
        url = "https://www.whoscored.com"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }
        try:
            response = self.session.get(url,headers = headers, impersonate = "chrome120", timeout = 30)
            soup = BeautifulSoup(response.text, 'html.parser')
            element = soup.select_one('script:-soup-contains("var allRegions")')
            raw_text = element.text.split("var allRegion= ")[0].strip()
            raw_text = raw_text.replace("var allRegions = ","").strip()
            raw_text = raw_text.rstrip(";, \n")
            new_list = json5.loads(raw_text)
        except Exception as e:
            print(f"(!) Connection/Parsing error: {e}")
        return new_list
    def get_league(self):  # scrapes whoscored.com -> Gets the leagues ids and names and urls out of it -> For each league it gets the years and the stage ids out of it and saves all of this in a json file named dict.json
        leagues = self.all_leagues()
        url = ""
        if self.country is not None:
            for element in leagues:
                if element['name'].lower() == self.country.lower():
                    for tournament in element['tournaments']:
                        if tournament['name'].lower() == self.name.lower():
                            url = tournament['url']
                            break
                    break

        else:
            for element in leagues:
                for tournament in element['tournaments']:
                    if tournament['name'].lower() == self.name.lower():
                        url = tournament['url']
                        break

        return url

    def get_fixtures(self):
        url = self.get_league()
        if url is  None:
            raise ValueError("Couldn't scrape whoscored.")

        full_url = "https://www.whoscored.com" + url

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }
        res = self.session.get(full_url, headers=headers,impersonate="chrome120")
        dictt = {}
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            full = soup.find(attrs = {"id" :"seasons","name":"seasons"})
            conts = full.contents
            listt = [x for x in conts if x != '\n']
            #A dictionary containing year : fixtures link. I will use the fixtures link to scrape the data out of it. Might store the resulting dictionary in a file later.
            for element in listt:
                link = "https://www.whoscored.com" + element['value']
                res1 = self.session.get(link, headers=headers, impersonate="chrome120")
                soup1 = BeautifulSoup(res1.text, 'html.parser')
                fixtures = soup1.find(attrs={"id": "link-fixtures"})
                new_element = {element.text: fixtures['href']}
                dictt.update(new_element)
        else:
            raise ValueError("nada")
        return dictt

    def get_matches(self): #Returns the list of the ids for the whole season.
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }
        fixtures = self.get_fixtures()
        seasons = self.season.split('/')
        months_to_scrape = [
            seasons[0] + "08", seasons[0] + "09", seasons[0] + "10", seasons[0] + "11", seasons[0] + "12",
            seasons[1] + "01", seasons[1] + "02", seasons[1] + "03", seasons[1] + "04", seasons[1] + "05",
            seasons[1] + "06", seasons[1] + "07"
        ]
        my_fixture = fixtures[self.season]
        stage_id = my_fixture.split('/')[8]
        match_ids = [] #A list holding matchs ids
        for month in months_to_scrape:
            url = f"https://www.whoscored.com/tournaments/{stage_id}/data/?d={month}"
            try:
                response = requests.get(url, headers = headers, impersonate="chrome120", timeout=30)
                data = response.json()
                for tourney in data.get('tournaments', []):
                    for match in tourney.get('matches', []):
                        match_ids.append(match['id'])
            except Exception as e:
                print(f"(!) Error fetching schedule for month: {month},{e}")
        return match_ids

    def get_data(self):
        match_ids = self.get_matches()
        urls_to_scrape = []
        for match_id in match_ids:
            url = f"https://www.whoscored.com/Matches/{match_id}/Live"
            urls_to_scrape.append(url)
        self.base_urls = urls_to_scrape
        return self.crawl()
    #def save_data(self): #--> Polymorph behavior

def get_infos(url):
    pattern = re.compile(r'matches/(\d+)/.*?/[^-]+-(.+?)-(\d{4}-\d{4})')
    match = pattern.search(url)
    id, league, season = "", "",""
    if match:
        id, league, season = match.group(1), match.group(2),match.group(3)
    return id, league, season

class SpadlConverter:
    def __init__(self,data_list, combined_df = None): #The input data must be in JSON format
        self.data_list = data_list
        self.combined_df = combined_df

    def parse(self):
        for data_point in self.data_list: #data point is in the format data,url of the match.
            url = data_point['url']
            data = data_point['data']
            home_team_id = int(data['home']['teamId'])
            home_team_name = (data['home']['name'])
            away_team_id = int(data['away']['teamId'])
            away_team_name = (data['away']['name'])
            teams = {
                home_team_id: home_team_name,
                away_team_id: away_team_name
            }
            id,league,season = (get_infos(url))
            temp_file = tempfile.NamedTemporaryFile(mode = 'w', suffix = '.json', delete = False)
            temp_path = temp_file.name
            json.dump(data, temp_file)
            temp_file.close()
            parser = WhoScoredParser(
                path = temp_path,
                competition_id = league,
                season_id = season,
                game_id = int(id),
            )
            df_events = pd.DataFrame.from_dict(parser.extract_events(), orient="index")
            df_events = df_events.merge(_eventtypesdf, on="type_id", how="left").reset_index(drop=True)
            df_spadl = convert_to_actions(df_events, home_team_id=home_team_id)
            df_spadl = pd.merge(df_spadl, spadlconfig.actiontypes_df(), on='type_id', how='inner') #added action name
            df_spadl = pd.merge(df_spadl, spadlconfig.results_df(), on='result_id', how='inner') #added result name
            df_spadl = pd.merge(df_spadl, spadlconfig.bodyparts_df(), on='bodypart_id', how='inner') ##added body part name
            players_names = data['playerIdNameDictionary']
            df_spadl['player_id'] = df_spadl['player_id'].apply(lambda x: int(x))
            df_spadl['player_id'] = df_spadl['player_id'].apply(lambda x: str(x))
            df_spadl['player_name'] = df_spadl['player_id'].map(players_names)
            df_spadl['team_name'] = df_spadl['team_id'].map(teams)
            self.combined_df = pd.concat(
                [self.combined_df, df_spadl],
                ignore_index=True
            )
        return self.combined_df

    def save(self, path = "../data/spadl"):
        self.combined_df.to_parquet(
            path,
            engine='pyarrow',
            compression='snappy',
            partition_cols=['game_id']
        )

class GstatesConverter:
    features_list = [
        fs.actiontype,
        fs.actiontype_onehot,
        fs.bodypart,
        fs.bodypart_onehot,
        fs.result,
        fs.result_onehot,
        fs.goalscore,
        fs.startlocation,
        fs.endlocation,
        fs.movement,
        fs.space_delta,
        fs.startpolar,
        fs.endpolar,
        fs.team,
        fs.time,
        fs.time_delta
    ]
    labels_list = [
        lab.scores,
        lab.concedes,
        lab.goal_from_shot
    ]
    def __init__(self,read_path = "../data/spadl", columns = None, filters = None):
        self.data = pd.read_parquet(
            read_path,
            engine='pyarrow',
            filters = filters #To filter out games by their ids.(ex: filters=[('game_id', '=', 1914251)])
        )
        cat_cols = self.data.select_dtypes(include=['category']).columns
        self.data[cat_cols] = self.data[cat_cols].astype('object') #converting game_id to string.
        unique_teams = self.data['team_id'].unique()
        self.home_team_id = unique_teams[0]
        if self.data is not None:
            print(f"The data of {len(self.data)} games loaded.")

    def convert_to_gamestate(self,match_data,home_team,nbr_of_previous_actions = 3, normalize = True): #Normalization stands for performing all action in the same playing direction
        gs = fs.gamestates(match_data, nb_prev_actions=nbr_of_previous_actions)
        if normalize:
            gamestates = fs.play_left_to_right(gs, home_team)
        return gamestates

    def compute_features(self,match_data,home_team, features = features_list):
        gs = self.convert_to_gamestate(match_data, home_team)
        X = pd.concat([fn(gs) for fn in features], axis=1)
        X = pd.concat([X, match_data['game_id']], axis=1)
        return X
    def compute_labels(self,match_data, labels = labels_list):
        Y = pd.concat([fn(match_data) for fn in labels], axis=1)
        Y = pd.concat([Y, match_data['game_id']], axis=1)
        return Y
    def convert(self, features = features_list, labels = labels_list):
        all_features = []
        all_labels = []
        for game_id, game_data in self.data.groupby('game_id'):
            home_team_id = game_data['team_id'].values[0]
            X = self.compute_features(game_data, home_team_id)
            Y = self.compute_labels(game_data)
            all_features.append(X)
            all_labels.append(Y)
        X_final = pd.concat(all_features)
        Y_final = pd.concat(all_labels)
        result = pd.concat([X_final, Y_final],axis = 1)
        result = result.loc[:, ~result.columns.duplicated()].copy()
        return result

    def save(self, path="../data/game_states"):
        res = self.convert()
        res.to_parquet(
            path,
            engine='pyarrow',
            compression='snappy',
            partition_cols=['game_id']
        )

def main():
    list = ["https://www.whoscored.com/matches/1914256/live/spain-laliga-2025-2026-real-madrid-athletic-club", "https://www.whoscored.com/matches/1914251/live/spain-laliga-2025-2026-sevilla-real-madrid"]
    scr = MatchScraper(list)
    data = scr.crawl()
    #lg = LeagueScraper("laliga","2025/2026","spain")
    #data = lg.get_data()
    cv = SpadlConverter(data_list = data)
    dff = cv.parse()

    cv.save()
    gss = GstatesConverter()
    gss.save()
if __name__ == "__main__":
    main()