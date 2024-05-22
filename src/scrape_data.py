import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# URL of the website containing the table
def scrape_data(url):
    # Send a GET request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve webpage. Status code: {response.status_code}")
    
    # parse HTML content and find the table
    soup = BeautifulSoup(response.content, 'html.parser')   
    table = soup.find('table')        
    if not table: 
        raise ValueError("Table not found on webpage.")      
        
    # store scraped data in these lists
    matchweek, home_team, home_xg, score, away_xg, away_team, match_reports = [], [], [], [], [], [], []

    
    # go through table -- exclude header row (tr = table row), start at 1: to exclude header
    for row in table.find_all('tr')[1:]:
        # Extract data from the cells using column names
        cur_matchweek = row.find('th', {'data-stat': 'gameweek'}).text.strip()
        cur_home_team = row.find('td', {'data-stat': 'home_team'}).text.strip()
        cur_home_xg = row.find('td', {'data-stat': 'home_xg'}).text.strip()
        cur_score = row.find('td', {'data-stat': 'score'}).text.strip()
        cur_away_xg = row.find('td', {'data-stat': 'away_xg'}).text.strip()
        cur_away_team = row.find('td', {'data-stat': 'away_team'}).text.strip()
        cur_match_report_link = row.find('td', {'data-stat': 'match_report'}).find('a', href=True)
        cur_match_report_url = cur_match_report_link['href'] if cur_match_report_link else ''
        
        # Append the extracted data to the lists
        if cur_matchweek:
            matchweek.append(cur_matchweek)
            home_team.append(cur_home_team)
            home_xg.append(cur_home_xg)
            score.append(cur_score)
            away_xg.append(cur_away_xg)
            away_team.append(cur_away_team)
            match_reports.append(cur_match_report_url)

    return {
        "Matchweek": matchweek,
        "Home Team": home_team,
        "Home XG": home_xg,
        "Score": score,
        "Away XG": away_xg,
        "Away Team": away_team,
        "Match Report": match_reports
    }

            
if __name__ == "__main__":
    try: 
        # get data from fbref
        url = 'https://fbref.com/en/comps/9/schedule/Premier-League-Scores-and-Fixtures'
        data = scrape_data(url)
        if not data: raise Exception("Data scrape failed")
        
        # scraped data -->  pandas dataframe --> csv
        df = pd.DataFrame(data)
        os.makedirs('data', exist_ok=True) # make directory if it doesn't exist
        df.to_csv('data/prem_data.csv', index=False)
        print("Data saved to data/prem_data.csv")
    except Exception as e: 
        print(f"ERROR: {e}")