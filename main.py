import logging
import os
import yaml # type: ignore
import pandas as pd
from src.data_preprocessing import clean_data
from src.scrape_data import scrape_data
import traceback

# init logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

if __name__ == "__main__":
    config = load_config('src/config.yaml')
    url = config['url']
    raw_data_path = config['raw_data_path']
    played_path = config['played_path']
    unplayed_path = config['unplayed_path']
    
    try: 
        # get data from fbref
        raw_data = scrape_data(url)
        if not raw_data: 
            raise Exception("Data scrape failed")
        
        # scraped data -->  pandas dataframe --> csv
        df = pd.DataFrame(raw_data)
        os.makedirs(os.path.dirname(raw_data_path), exist_ok=True) # make directory if it doesn't exist
        df.to_csv(raw_data_path, index=False)
        logging.info(f"Data saved to {raw_data_path} from {url} in main")

        # clean data and format columns
        played, unplayed = clean_data(raw_data_path)
        played.to_csv(played_path, index=False)
        unplayed.to_csv(unplayed_path, index=False)
        logging.info(f"Data saved successfully to {played_path}, {unplayed_path}")


    except Exception as e:
        logging.error(f"{e}")
        logging.error(traceback.format_exc())
