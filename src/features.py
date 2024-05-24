import pandas as pd
import numpy as np
import logging
import traceback

logging.basicConfig(level = logging.INFO, format='%(asctime)s - %(levelname)s -  %(message)s')

def home_strength(played_csv_path):
    """
    calculate the home team's strength
    input: dataframes of played and unplayed results
    output: home team avg goals scored & conceded, and wins    
    """
    played = pd.read_csv(played_csv_path)
    logging.info(f"Data loaded successfully from {played_csv_path} in home_team_strength")

    try:
        home_team_strength = played.groupby('Home_Team').agg(
            goals_scored=('Home Goals', 'mean'),
            goals_conceded=('Away Goals', 'mean'),
            home_wins=('Home Goals', lambda x: (x > played['Away Goals'])).sum()
            ).reset_index()
        logging.info("Calculated home strength feature")
        return home_team_strength
    except Exception as e:
        logging.error(f"Error calculating home strength feature: {e}")


def away_strength(played_csv_path):
    """
    calculate the away team's strength
    input: dataframes of played and unplayed results
    output: away team avg goals scored & conceded, and wins
    """
    played = pd.read_csv(played_csv_path)
    logging.info(f"Data loaded successfully from {played_csv_path} in home_team_strength")
    try:
        away_team_strength = df.groupby('Away Team').agg(
            avg_goals_scored_away=('Away Goals', 'mean'),
            avg_goals_conceded_away=('Home Goals', 'mean'),
            away_wins=('Away Goals', lambda x: (x > df.loc[x.index, 'Home Goals']).sum())
        ).reset_index()
        logging.info("Calculated away team strength successfully.")
        return away_team_strength
    except Exception as e:
        logging.error(f"Error calculating away team strength: {e}")
        return pd.DataFrame()
