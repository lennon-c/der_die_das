from dwds.update_freq import get_lemmata_to_update
import os 
import pickle


def run():
    """get updates from local package dwds and save them in pickle file
    
    to be run in the local machine
    """
    lemmata_freq = get_lemmata_to_update()
    lemmata_dict = lemmata_freq.to_dict('records')
    with open('lemmata_dict.pkl', 'wb') as f:
        pickle.dump(lemmata_dict, f)

    print('saved in folder:', os.getcwd())