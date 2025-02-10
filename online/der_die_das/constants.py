
from .models import Level, Lemma, Gender, Entry # type: ignore


ALL_ENTRIES = Entry.objects.select_related().all()
ALL_LEMMATA = Lemma.objects.select_related().all()

# ids / lists
GENDERS = Gender.objects.values_list('id','article') 
LEVELS  = Level.objects.all().order_by('level').values_list('id','level')
LEVELS_ID = Level.objects.values_list('id', flat= True)
FREQUENCIES = Lemma.objects.values_list('frequency', flat=True).distinct().order_by('frequency')

# dictionary with level as key and lemmata as values
LEMMATA_LEVELS = {level:ALL_LEMMATA.filter(level=level).all()
                   for level in LEVELS_ID }
LEMMATA_ID_LEVELS = {level: LEMMATA_LEVELS[level].values_list('id', flat=True)
                      for level in LEVELS_ID}
LEMMATA_LEN_LEVELS = {level: LEMMATA_LEVELS[level].count() 
                      for level in LEVELS_ID}

# dictionaries from id to label
LEVELS_MAP = { str(id): label for id, label in Level.objects.values_list('id','level')} 
ARTICLES_MAP = { str(id): label for id, label in GENDERS}


# # for bulk create (at script run this constant are evaluated, which is problematic)
# ALL_ENTRIES = []
# ALL_LEMMATA = []
# GENDERS= []
# LEMMATA_LEVELS =dict() 
# LEMMATA_ID_LEVELS=dict()
# LEMMATA_LEN_LEVELS=dict() 
# LEVELS_MAP=dict()
# ARTICLES_MAP=dict()
# FREQUENCIES = []
# LEVELS = []