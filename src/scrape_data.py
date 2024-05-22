import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import traceback

# init logging
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s -  %(message)s')

# define stat variables
DATA_STAT_GAMEWEEK = 'gameweek'
DATA_STAT_HOME_TEAM = 'home_team'
DATA_STAT_HOME_XG = 'home_xg'
DATA_STAT_SCORE = 'score'
DATA_STAT_AWAY_XG = 'away_xg'
DATA_STAT_AWAY_TEAM = 'away_team'
DATA_STAT_MATCH_REPORT = 'match_report'


# URL of the website containing the table
def scrape_data(url):
    try: 
        # send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status() # check HTTP errors
        
        
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
            cur_matchweek = row.find('th', {'data-stat': DATA_STAT_GAMEWEEK}).text.strip()
            cur_home_team = row.find('td', {'data-stat': DATA_STAT_HOME_TEAM}).text.strip()
            cur_home_xg = row.find('td', {'data-stat': DATA_STAT_HOME_XG}).text.strip()
            cur_score = row.find('td', {'data-stat': DATA_STAT_SCORE}).text.strip()
            cur_away_xg = row.find('td', {'data-stat': DATA_STAT_AWAY_XG}).text.strip()
            cur_away_team = row.find('td', {'data-stat': DATA_STAT_AWAY_XG}).text.strip()
            cur_match_report_link = row.find('td', {'data-stat': DATA_STAT_MATCH_REPORT}).find('a', href=True)
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

    except requests.RequestException as e:
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())
        return None
    except ValueError as e:
        logging.error(f"ERROR: {e}")
        logging.error(traceback.format_exc())
        return None