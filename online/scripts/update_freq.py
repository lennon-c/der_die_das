from der_die_das.models import Lemma 
import pickle

FILE = 'lemmata_dict.pkl'

def run():
    """get list of dictionaries with the lemmata to be updated
    
    To be run in PAW
    """
    with open(FILE, 'rb') as f:
        lemmata_dict = pickle.load(f)
    
    for n, dic in enumerate(lemmata_dict):
        lemma_text = dic['lemma']
        freq = dic['freq']
        print(n, lemma_text, freq)
        Lemma.objects.filter(lemma=lemma_text).update(frequency=freq)

 
