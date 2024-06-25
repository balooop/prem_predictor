import pandas as pd
import numpy as np
import logging
import traceback
import os
import yaml
from typing import Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants for column names
COLUMN_MATCHWEEK = 'Matchweek'
COLUMN_HOME_XG = 'Home XG'
COLUMN_AWAY_XG = 'Away XG'
COLUMN_SCORE = 'Score'
COLUMN_HOME_GOALS = 'Home Goals'
COLUMN_AWAY_GOALS = 'Away Goals'

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

def clean_data(raw_data_filepath: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Loads and preprocesses match data from a CSV file.
    
    Args:
        raw_data_filepath (str): Path to the CSV containing match data.
    
    Returns:
        tuple: Contains two pandas DataFrames (played, unplayed).
    """
    try:
        # load data
        raw_data = pd.read_csv(raw_data_filepath)
        raw_data = raw_data.dropna(how='all')
        logging.info(f"Data loaded successfully from {raw_data_filepath}. Removed empty rows.")

        # adjust types
        raw_data[COLUMN_MATCHWEEK] = raw_data[COLUMN_MATCHWEEK].astype(int)
        raw_data[COLUMN_HOME_XG] = raw_data[COLUMN_HOME_XG].astype(float)
        raw_data[COLUMN_AWAY_XG] = raw_data[COLUMN_AWAY_XG].astype(float)

        # split data into played and unplayed games based on 'Score' availability
        played = raw_data[raw_data[COLUMN_SCORE].notna()].copy()
        unplayed = raw_data[raw_data[COLUMN_SCORE].isna()].copy()

        # process scores for played games
        if not played.empty:
            goals = played[COLUMN_SCORE].str.split('–', expand=True)
            played[COLUMN_HOME_GOALS] = goals[0].astype(int)
            played[COLUMN_AWAY_GOALS] = goals[1].astype(int)
            played.drop(columns=[COLUMN_SCORE], inplace=True)

        # set goals to NaN for unplayed games
        if not unplayed.empty:
            unplayed[COLUMN_HOME_GOALS] = np.nan
            unplayed[COLUMN_AWAY_GOALS] = np.nan
            unplayed.drop(columns=[COLUMN_SCORE], inplace=True)

        logging.info("Data preprocessing completed successfully.")
        return played, unplayed

    except (ValueError, TypeError) as e:
        logging.error(f"Error in data types: {e}")
        traceback.print_exc()
        return None, None
    except Exception as e:
        logging.error(f"An unexpected error occurred during data preprocessing: {e}")
        traceback.print_exc()
        return None, None

if __name__ == "__main__":
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, 'config.yaml')
        config = load_config(config_path)

        raw_data_file = os.path.join(current_dir, '..', config['raw_data_path'])
        played_path = os.path.join(current_dir, '..', config['played_path'])
        unplayed_path = os.path.join(current_dir, '..', config['unplayed_path'])

        played, unplayed = clean_data(raw_data_file)
        if played is not None and unplayed is not None:
            print(f"Played games: {len(played)}")
            print(f"Unplayed games: {len(unplayed)}")
            
            # Save data only when running this file directly
            played.to_csv(played_path, index=False)
            unplayed.to_csv(unplayed_path, index=False)
            logging.info(f"Played games saved to {played_path}")
            logging.info(f"Unplayed games saved to {unplayed_path}")
        else:
            print("Data processing failed.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        traceback.print_exc()