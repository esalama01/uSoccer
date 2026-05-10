"""

    This script will:
        1) Traverse {converter/data} repo
        2) For each league: 
            2-1)traverse each year
            2-2)For each year:
                2-2-1)Convert every single match to spadl data type. And save the the corresponding file to converter/data/Correspondig_league/corresponding_year.
"""

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import os

#Get all the subtrees at {converter/data}

repos = set()

for root, dirs, files in os.walk('../../scraper/data'):
    repos.add(root)


def main():
    for repo in repos:
        print(repo)

if __name__ == "__main__":
    main()