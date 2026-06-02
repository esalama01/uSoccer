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

initial_evs = json5.loads("{\"shotSixYardBox\":0,\"shotPenaltyArea\":1,\"shotOboxTotal\":2,\"shotOpenPlay\":3,\"shotCounter\":4,\"shotSetPiece\":5,\"shotDirectCorner\":6,\"shotOffTarget\":7,\"shotOnPost\":8,\"shotOnTarget\":9,\"shotsTotal\":10,\"shotBlocked\":11,\"shotRightFoot\":12,\"shotLeftFoot\":13,\"shotHead\":14,\"shotObp\":15,\"goalSixYardBox\":16,\"goalPenaltyArea\":17,\"goalObox\":18,\"goalOpenPlay\":19,\"goalCounter\":20,\"goalSetPiece\":21,\"penaltyScored\":22,\"goalOwn\":23,\"goalNormal\":24,\"goalRightFoot\":25,\"goalLeftFoot\":26,\"goalHead\":27,\"goalObp\":28,\"shortPassInaccurate\":29,\"shortPassAccurate\":30,\"passCorner\":31,\"passCornerAccurate\":32,\"passCornerInaccurate\":33,\"passFreekick\":34,\"passBack\":35,\"passForward\":36,\"passLeft\":37,\"passRight\":38,\"keyPassLong\":39,\"keyPassShort\":40,\"keyPassCross\":41,\"keyPassCorner\":42,\"keyPassThroughball\":43,\"keyPassFreekick\":44,\"keyPassThrowin\":45,\"keyPassOther\":46,\"assistCross\":47,\"assistCorner\":48,\"assistThroughball\":49,\"assistFreekick\":50,\"assistThrowin\":51,\"assistOther\":52,\"dribbleLost\":53,\"dribbleWon\":54,\"challengeLost\":55,\"interceptionWon\":56,\"clearanceHead\":57,\"outfielderBlock\":58,\"passCrossBlockedDefensive\":59,\"outfielderBlockedPass\":60,\"offsideGiven\":61,\"offsideProvoked\":62,\"foulGiven\":63,\"foulCommitted\":64,\"yellowCard\":65,\"voidYellowCard\":66,\"secondYellow\":67,\"redCard\":68,\"turnover\":69,\"dispossessed\":70,\"saveLowLeft\":71,\"saveHighLeft\":72,\"saveLowCentre\":73,\"saveHighCentre\":74,\"saveLowRight\":75,\"saveHighRight\":76,\"saveHands\":77,\"saveFeet\":78,\"saveObp\":79,\"saveSixYardBox\":80,\"savePenaltyArea\":81,\"saveObox\":82,\"keeperDivingSave\":83,\"standingSave\":84,\"closeMissHigh\":85,\"closeMissHighLeft\":86,\"closeMissHighRight\":87,\"closeMissLeft\":88,\"closeMissRight\":89,\"shotOffTargetInsideBox\":90,\"touches\":91,\"assist\":92,\"ballRecovery\":93,\"clearanceEffective\":94,\"clearanceTotal\":95,\"clearanceOffTheLine\":96,\"dribbleLastman\":97,\"errorLeadsToGoal\":98,\"errorLeadsToShot\":99,\"intentionalAssist\":100,\"interceptionAll\":101,\"interceptionIntheBox\":102,\"keeperClaimHighLost\":103,\"keeperClaimHighWon\":104,\"keeperClaimLost\":105,\"keeperClaimWon\":106,\"keeperOneToOneWon\":107,\"parriedDanger\":108,\"parriedSafe\":109,\"collected\":110,\"keeperPenaltySaved\":111,\"keeperSaveInTheBox\":112,\"keeperSaveTotal\":113,\"keeperSmother\":114,\"keeperSweeperLost\":115,\"keeperMissed\":116,\"passAccurate\":117,\"passBackZoneInaccurate\":118,\"passForwardZoneAccurate\":119,\"passInaccurate\":120,\"passAccuracy\":121,\"cornerAwarded\":122,\"passKey\":123,\"passChipped\":124,\"passCrossAccurate\":125,\"passCrossInaccurate\":126,\"passLongBallAccurate\":127,\"passLongBallInaccurate\":128,\"passThroughBallAccurate\":129,\"passThroughBallInaccurate\":130,\"passThroughBallInacurate\":131,\"passFreekickAccurate\":132,\"passFreekickInaccurate\":133,\"penaltyConceded\":134,\"penaltyMissed\":135,\"penaltyWon\":136,\"passRightFoot\":137,\"passLeftFoot\":138,\"passHead\":139,\"sixYardBlock\":140,\"tackleLastMan\":141,\"tackleLost\":142,\"tackleWon\":143,\"cleanSheetGK\":144,\"cleanSheetDL\":145,\"cleanSheetDC\":146,\"cleanSheetDR\":147,\"cleanSheetDML\":148,\"cleanSheetDMC\":149,\"cleanSheetDMR\":150,\"cleanSheetML\":151,\"cleanSheetMC\":152,\"cleanSheetMR\":153,\"cleanSheetAML\":154,\"cleanSheetAMC\":155,\"cleanSheetAMR\":156,\"cleanSheetFWL\":157,\"cleanSheetFW\":158,\"cleanSheetFWR\":159,\"cleanSheetSub\":160,\"goalConcededByTeamGK\":161,\"goalConcededByTeamDL\":162,\"goalConcededByTeamDC\":163,\"goalConcededByTeamDR\":164,\"goalConcededByTeamDML\":165,\"goalConcededByTeamDMC\":166,\"goalConcededByTeamDMR\":167,\"goalConcededByTeamML\":168,\"goalConcededByTeamMC\":169,\"goalConcededByTeamMR\":170,\"goalConcededByTeamAML\":171,\"goalConcededByTeamAMC\":172,\"goalConcededByTeamAMR\":173,\"goalConcededByTeamFWL\":174,\"goalConcededByTeamFW\":175,\"goalConcededByTeamFWR\":176,\"goalConcededByTeamSub\":177,\"goalConcededOutsideBoxGoalkeeper\":178,\"goalScoredByTeamGK\":179,\"goalScoredByTeamDL\":180,\"goalScoredByTeamDC\":181,\"goalScoredByTeamDR\":182,\"goalScoredByTeamDML\":183,\"goalScoredByTeamDMC\":184,\"goalScoredByTeamDMR\":185,\"goalScoredByTeamML\":186,\"goalScoredByTeamMC\":187,\"goalScoredByTeamMR\":188,\"goalScoredByTeamAML\":189,\"goalScoredByTeamAMC\":190,\"goalScoredByTeamAMR\":191,\"goalScoredByTeamFWL\":192,\"goalScoredByTeamFW\":193,\"goalScoredByTeamFWR\":194,\"goalScoredByTeamSub\":195,\"aerialSuccess\":196,\"duelAerialWon\":197,\"duelAerialLost\":198,\"offensiveDuel\":199,\"defensiveDuel\":200,\"bigChanceMissed\":201,\"bigChanceScored\":202,\"bigChanceCreated\":203,\"overrun\":204,\"successfulFinalThirdPasses\":205,\"punches\":206,\"penaltyShootoutScored\":207,\"penaltyShootoutMissedOffTarget\":208,\"penaltyShootoutSaved\":209,\"penaltyShootoutSavedGK\":210,\"penaltyShootoutConcededGK\":211,\"throwIn\":212,\"subOn\":213,\"subOff\":214,\"defensiveThird\":215,\"midThird\":216,\"finalThird\":217,\"pos\":218}")
events = {v: k for k, v in initial_evs.items()}
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
    def __init__(self, league_name, league_season, country = None): #league season must be in (xxxx-yyyy) format
        #It's much better if the league country was provided.
        season_pattern = r"^(\d{4})/\d{4}$"
        name_pattern = r""
        if not re.fullmatch(season_pattern, league_season):
            raise ValueError("season must be in (xxxx/yyyy) format.")
        #If league_name not in leagues, i must call get_league on it.

        self.name = league_name
        self.season = league_season
        self.country = country
        super().__init__(base_urls=[])

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
            element = soup.select_one('script:-soup-contains("var allRegions")')
            raw_text = element.text.split("var allRegion= ")[0].strip().replace("var allRegions = ","")
            txtt = raw_text.split(",\n")
            new_list = []
            for element in txtt:
                new_list.append(json5.loads(element))
            return new_list
        except Exception as e:
            print(f"(!) Connection/Parsing error: {e}")
            return None

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
        if url is None:
            raise ValueError("Couldn't scrape whoscored.")

        full_url = "https://www.whoscored.com" + url

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "referer": "https://www.google.com/"
        }

        res = requests.get(full_url, headers=headers,impersonate="chrome120")
        soup = BeautifulSoup(res.text, 'html.parser')
        full = soup.find(attrs={"id": "seasons", "name": "seasons"})
        listt = [x for x in full.contents if x != '\n']
        dictt = {} #A dictionary containing year : fixtures link. I will use the fixtures link to scrape the data out of it. Might store the resulting dictionary in a file later.
        for element in listt:
            link = "https://www.whoscored.com" + element['value']
            res1 = requests.get(link, headers=headers, impersonate="chrome120")
            soup1 = BeautifulSoup(res1.text, 'html.parser')
            fixtures = soup1.find(attrs={"id": "link-fixtures"})
            new_element = {element.text: fixtures['href']}
            dictt.update(new_element)
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
    pattern = re.compile(r'^[^-]+-(.+?)-(\d{4}-\d{4})')
    match = pattern.search(url)
    id, league, season = "", ""
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
            df_spadl['type_name'] = df_spadl['action_id'].map(events) #added events type names
            players_names = data['playerIdNameDictionary']
            df_spadl['player_id'] = df_spadl['player_id'].apply(lambda x: int(x))
            df_spadl['player_id'] = df_spadl['player_id'].apply(lambda x: str(x))
            df_spadl['player_name'] = df_spadl['player_id'].map(players_names)


def main():
    list = ["https://www.whoscored.com/matches/1914256/live/spain-laliga-2025-2026-real-madrid-athletic-club"]
    scr = MatchScraper(list)
    data = scr.crawl()
    print(data[0]['url'])

if __name__ == "__main__":
    main()