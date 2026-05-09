import json
import pandas as pd
from socceraction.data.opta.parsers import WhoScoredParser
from socceraction.spadl.opta import convert_to_actions
from socceraction.data.opta.loader import _eventtypesdf


file_path = r"/home/esalama01/projects/uSoccer/scraper/data/La Liga/spain-laliga-2023-2024/1734624_match_data.json"

with open(file_path, "r", encoding="utf-8") as f:
    json_file = json.load(f)

"""
var optaCompetitions = [
	{
		header: "UK & Scotland",
		items: [
			{name: "English Barclays Premier League", id:8},
			{name: "English Football League Championship", id:10},
			{name: "Scottish Premiership", id:14},
			{name: "English Football League - League 1", id:11},
			{name: "English Football League - League 2", id:12},
			{name: "English FA Cup", id:1},
			{name: "English League Cup", id:2},
			{name: "English Football League Trophy", id:7}
		]
	},
	{
		header: "European and International",
		items : [
			{name: "World Cup", id:4},
			{name: "Champions League", id:5},
			{name: "UEFA Europa League", id: 6},
			{name: "Japanese J-League", id:20},
			{name: "Italian Serie A", id:21},
			{name: "German Bundesliga", id:22},
			{name: "Spanish La Liga", id:22},
			
		]
	}
];
"""

#Get the home team id

home_team_id = int(json_file["home"]["teamId"])

parser = WhoScoredParser(
    file_path,
    competition_id="La Liga",
    season_id= ""
)