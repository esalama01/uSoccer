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
#Get all the subtrees at {converter/data}

initial_dir = r"../../scraper/data"

whoscored_leagues = [
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
values = whoscored_leagues

map = dict(zip(keys, values))

"""
def create_subd(name):
    path = Path(f"../data/{map[name]}")
    # Create the directories
    path.mkdir(parents=True, exist_ok=True)


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

def convert(file_path): #takes a folder as input and converts every file in it to spadl.
    paths = [] 
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():
                path.append(entry.path)
"""
def create_subdirs(name, corr_year): #returns the name of thhe created subdirectory, and year of the next sub to fill it in the whoscored parser.(input like : Epl/england-premier-league-2025-2026)
    pattern = r"\d{4}"
    years = re.findall(pattern, corr_year)
    year = "-".join(years)
    path = Path(f"../data/{map[name]}/{year}")
    # Create the directories
    path.mkdir(parents=True, exist_ok=True)
    return map[name], year

def main():
    for repo in repos:
        print(repo)
    print("---------------------------------------------------------------")
    for repo in sub_repos:
        print(repo)


if __name__ == "__main__":
    main()