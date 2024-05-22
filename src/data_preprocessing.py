import pandas as pd
import numpy as np
import logging
import traceback

# init logging
logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s -  %(message)s')
    
# define column variables
COLUMN_MATCHWEEK = 'Matchweek'
COLUMN_HOME_XG = 'Home XG'
COLUMN_AWAY_XG = 'Away XG'
COLUMN_SCORE = 'Score'
COLUMN_HOME_GOALS = 'Home Goals'
COLUMN_AWAY_GOALS = 'Away Goals'

def clean_data(raw_data_path):
    """
    loads data from csv and preprocess to fix types
    args: 
        csv_path (str): Path to CSV containing match data
    returns:
        played, unplayed (pd.DataFrame): played & unplayed games. "Home Goals" & "Away Goals" for unplayed games are NaN
    """
    raw_data = pd.read_csv(raw_data_path)
    logging.info(f"Data loaded successfully from {raw_data_path} in clean_data")

    # initialize DataFrame for raw_data
    try: 
        # adjust types
        raw_data[COLUMN_MATCHWEEK] = raw_data[COLUMN_MATCHWEEK].astype(int)
        raw_data[COLUMN_HOME_XG] = raw_data[COLUMN_HOME_XG].astype(float)
        raw_data[COLUMN_AWAY_XG] = raw_data[COLUMN_AWAY_XG].astype(float)
        
        # separate for processing scores
        played = raw_data[raw_data[COLUMN_SCORE].notnull()].copy()
        unplayed = raw_data[raw_data[COLUMN_SCORE].isnull()].copy()
        del raw_data

        # split home & away for played games
        goals = played[COLUMN_SCORE].str.split('–', expand=True)
            
        if not played.empty:
            played[COLUMN_HOME_GOALS] = goals[0].astype(int)
            played[COLUMN_HOME_GOALS] = goals[1].astype(int)
        
        del goals

        if not unplayed.empty:
            # unplayed games have NaN scores (to be predicted)
            unplayed[COLUMN_HOME_GOALS] = np.nan
            unplayed[COLUMN_AWAY_GOALS] = np.nan
        
        # clean
        played.drop(columns=[COLUMN_SCORE], inplace=True)
        unplayed.drop(columns=[COLUMN_SCORE], inplace=True)

        logging.info("Successfully initialized played and unplayed tables")
        return played, unplayed
    
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        logging.error(traceback.format_exc())

    except pd.errors.EmptyDataError as e:
        logging.error(f"Empty data: {e}")
        logging.error(traceback.format_exc())

    except Exception as e: 
        logging.error(f"{e}")
        logging.error(traceback.format_exc())
