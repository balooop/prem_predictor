import requests
from requests import RequestException 
import yaml
import logging
import traceback
import validators
import os

import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

# Configure logging to include the level, time, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants for data statistics
DATA_STAT_GAMEWEEK = 'gameweek'
DATA_STAT_DATE = 'date'
DATA_STAT_HOME_TEAM = 'home_team'
DATA_STAT_HOME_XG = 'home_xg'
DATA_STAT_SCORE = 'score'
DATA_STAT_AWAY_XG = 'away_xg'
DATA_STAT_AWAY_TEAM = 'away_team'
DATA_STAT_MATCH_REPORT = 'match_report'

def load_config(config_path: str) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Loaded configuration.

    Raises:
        FileNotFoundError: If the config file is not found.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except (FileNotFoundError, yaml.YAMLError) as e:
        logging.error(f"Error loading config: {e}")
        raise

def scrape_data(url: str) -> Optional[Dict[str,list]]:
    """
    Scrapes match data from a specified URL.
    
    Args:
        url (str): URL to scrape data from.

    Returns:
        dict: Dictionary containing scraped match data organized by categories.
    """
    if not validators.url(url):
        logging.error(f"Invalid URL: {url}")
        return None

    # HTTP request to url
    try:
        with requests.get(url, timeout=10) as response:
            response.raise_for_status()
            logging.info("Successfully retrieved data from URL")
    except RequestException as e:
        logging.error(f"HTTP error occurred: {e}")
        traceback.print_exc()
        return None
    
    # parse table & store in table
    try:  
        # find the table in the webpage
        soup = BeautifulSoup(response.content, 'html.parser')  
        table = soup.find('table')
        if not table:
            raise ValueError("Table not found on webpage.")
        logging.info("Successfully parsed HTML and found table")
        
        # initialize list to store data
        data: Dict[str, List[str]] = {
            "Matchweek": [], "Date": [], "Home Team": [], "Home XG": [],
            "Score": [], "Away XG": [], "Away Team": [], "Match Report": []
        }

        cur_matchweek, cur_date = "", ""
        # process rows in the webpage (start at 1: to exclude header)
        for row in table.find_all('tr')[1:]:
            # special cases, matchweek & date
            matchweek = row.find('th', {'data-stat': DATA_STAT_GAMEWEEK}).text.strip() 
            date = row.find('td', {'data-stat': DATA_STAT_DATE}).text.strip() 
            # if we find a matchweek / date, set them. otherwise, if blank, use previous
            cur_matchweek = matchweek if matchweek else cur_matchweek
            cur_date = date if date else cur_date 
            data["Matchweek"].append(cur_matchweek) 
            data["Date"].append(cur_date)

            #standard fields
            data["Home Team"].append(row.find('td', {'data-stat': DATA_STAT_HOME_TEAM}).text.strip())
            data["Home XG"].append(row.find('td', {'data-stat': DATA_STAT_HOME_XG}).text.strip())
            data["Score"].append(row.find('td', {'data-stat': DATA_STAT_SCORE}).text.strip())
            data["Away XG"].append(row.find('td', {'data-stat': DATA_STAT_AWAY_XG}).text.strip())
            data["Away Team"].append(row.find('td', {'data-stat': DATA_STAT_AWAY_TEAM}).text.strip())

            # special case, match report link -- append URL if found
            match_report_link = row.find('td', {'data-stat': DATA_STAT_MATCH_REPORT}).find('a', href=True)
            data["Match Report"].append(match_report_link['href'] if match_report_link else '')
            
        logging.info(f"Data scraped successfully. Total rows: {len(data['Matchweek'])}")
        return data
    
    except Exception as e:                                      
        logging.error(f"An error occurred while parsing data: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'config.yaml')
        config = load_config(config_path)
        
        url = config['url']
        raw_data_path = os.path.join(current_dir, '..', config['raw_data_path'])
        
        result = scrape_data(url)
        if result:
            df = pd.DataFrame(result)
            print("Success\n", df.head(), "\nShape:", df.shape)
            
            df.to_csv(raw_data_path, index=False)
            logging.info(f"Data saved to {raw_data_path}")
        else:
            logging.error("Data scraping failed")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        traceback.print_exc()