import pandas as pd
import numpy as np

def clean_data(csv_path):
    """
    loads data from csv and preprocess to fix types
    args: 
        csv_path (str): Path to CSV containing match data
    returns:
        played, unplayed (pd.DataFrame): played & unplayed games. "Home Goals" & "Away Goals" for unplayed games are NaN
    """
    # initialize DataFrame for prem_data
    prem_data = pd.read_csv(csv_path)
    print("prem_data: \n", prem_data.head())

    # adjust types
    prem_data['Matchweek'] = prem_data['Matchweek'].astype(int)
    prem_data.loc[:, 'Home XG'] = prem_data['Home XG'].astype(float)
    prem_data.loc[:, 'Away XG'] = prem_data['Away XG'].astype(float)
    print("prem_data: \n", prem_data.head())
    
    # separate for processing scores
    played = prem_data[prem_data['Score'].notnull()].copy()
    unplayed = prem_data[prem_data['Score'].isnull()].copy()

    print("played: \n", played.head())
    print("unplayed: \n", played.head())
    # split home & away for played games

    goals = played['Score'].str.split('-', expand=True)
    
    # print("Split result:\n", goals.head())
    
    played.loc[:, 'Home Goals'] = goals[0].astype(int)
    played.loc[:, 'Away Goals'] = goals[1].astype(int)

    # unplayed games have NaN scores (to be predicted)
    unplayed.loc[:, 'Home Goals'] = np.nan
    unplayed.loc[:, 'Away Goals'] = np.nan
    
    # clean
    played = played.drop(columns=['Score'])
    unplayed = unplayed.drop(columns=['Score'])
    del prem_data
    del goals

    return played, unplayed

if __name__ == "__main__":
    csv_path = 'data/prem_data.csv'
    played, unplayed = clean_data(csv_path)
    
    # Optional: Print statements to verify the results
    print(f"Played games:\n{played.head()}")
    print(f"Unplayed games:\n{unplayed.head()}")
