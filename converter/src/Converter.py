"""

    This script will:
        1) Traverse {converter/data} repo
        2) For each league: 
            2-1)traverse each year
            2-2)For each year:
                2-2-1)Convert every single match to spadl data type. And save the the corresponding file to converter/data/Correspondig_league/corresponding_year.
"""

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import json
import re
import pandas as pd
from socceraction.data.opta.parsers import WhoScoredParser
from socceraction.spadl.opta import convert_to_actions
from socceraction.data.opta.loader import _eventtypesdf
import os
from pathlib import Path


"""

def scan_dir(path):
    repos = set()
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                repos.add(entry.name) #--> Outputs a list of all sub_repos in my path
    for repo in repos:


repos = scan_dir(initial_dir)
sub_repos = set()

for repo in repos:
    path = fr"../../scraper/data/{repo}"
    new_repos = scan_dir(path)
    for n_repo in new_repos:
        sub_repos.add(n_repo)

def convert(file_path): #takes a file as input and converts it to csv spadl.
    paths = [] 
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():
                path.append(entry.path)
"""

def create_subdirs(name, corr_year): #returns the name of thhe created subdirectory, and year of the next sub to fill it in the whoscored parser.(input like : Epl/england-premier-league-2025-2026)
    values = [
    "ITA-Serie A",
    "ENG-Premier League",
    "INT-World Cup",
    "GER-Bundesliga",
    "POR-Liga Portugal",
    "NED-Eredivisie",
    "AMER-Copa America",
    "ESP-La Liga",
    "AFR-Africa Cup of Nations",
    "EUR-Champions League",
    "FRA-Ligue 1",
    "EUR-Euro"
    ]
    keys = ["Serie-a",
    "Epl",
    "World Cup",
    "Bundesliga",
    "Liga Portugal",
    "Netherlands Eredivisie",
    "Copa America",
    "La Liga,"
    "Afcon",
    "Ucl",
    "Ligue-1",
    "Euro"]
    map = dict(zip(keys, values))
    pattern = r"\d{4}"
    years = re.findall(pattern, corr_year)
    year = "-".join(years)
    path = Path(f"../data/{map[name]}/{year}")
    # Create the directories
    path.mkdir(parents=True, exist_ok=True)
    
    return map[name], year, path

def convert(file_path, file_name, comp_id, sea_id): #takes a file as input and converts it to csv spadl and returns the csv.
    
    with open(file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    home_team_id = int(json_data["home"]["teamId"])
    
    pattern = r"^\d+(?=_)"

    match = re.search(pattern, file_name)

    if match:
        id = match.group()

    parser = WhoScoredParser(
        file_path,
        competition_id= comp_id,
        season_id= sea_id, 
        game_id=id,
    )
    df_events = pd.DataFrame.from_dict(parser.extract_events(), orient="index") #extract events returns a dictionary with all available events.
    df_events = df_events.merge(_eventtypesdf, on="type_id", how="left").reset_index(drop=True) ##_eventtypesdf converts the whoscored events types to opta's --> Gets them ready for conversion 
    
    df_spadl = convert_to_actions(df_events, home_team_id=home_team_id) #Converts opta events to spadl actions.

    return df_spadl



def traversal():
    initial_dir = r"../../scraper/data"
    with os.scandir(initial_dir) as entries:
        for entry in entries:
            if entry.is_dir():
                with os.scandir(entry.path) as sub_entries:
                    for sub_entry in sub_entries:
                        league, year, new_path = create_subdirs(entry.name, sub_entry.name)
                        with os.scandir(sub_entry.path) as file_entries:
                            for file in file_entries:
                                if file.is_file():
                                    convert(file.path, file.name, league, year)

def main():
    for repo in repos:
        print(repo)
    print("---------------------------------------------------------------")
    for repo in sub_repos:
        print(repo)


if __name__ == "__main__":
    main()