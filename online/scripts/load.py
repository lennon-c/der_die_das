from der_die_das.models import Level, Type_Entry, Gender, Spelling,  Lemma, Entry, Entry_Gender, Entry_Spelling     # type: ignore
from dwds.entries_for_database import labels, GENDER_ARTICLE, lemma_level_freq, entry_level_freq

def delete_records():
        for table in Level, Type_Entry, Gender, Spelling, Lemma, Entry, Entry_Gender, Entry_Spelling,:
            table.objects.all().delete()


def run():

    delete_records()
    dic = labels()

    genders = dict()
    for g in dic['gender']:
        genders[g] = Gender.objects.create(gender=g, article=GENDER_ARTICLE[g])

    types = dict()
    for t in dic['type_name']:
        types[t] = Type_Entry.objects.create(type_name=t)

    levels = dict()
    for l in dic['level']:
        levels[l] = Level.objects.create(level=l)
        
    # lemmata list of dicts
    lemmata_list = lemma_level_freq()
    lemmata = [Lemma(**{'lemma': l['lemma'],
                        'level': levels[l['level']] if l['level'] else None,
                        'frequency': l['frequency']
                        }) for l in lemmata_list ]
    
    Lemma.objects.bulk_create(lemmata)
 
    entries_dicts = entry_level_freq()
    entries = list()
    spellings = dict()
    entries_genders = list()
    entries_spellings = list()
    for n,e in enumerate(entries_dicts):
        # if n == 10:
        #     break
        # print(e['lemma'])
        lemma = Lemma.objects.get(lemma=e['lemma'])
        entry = Entry(lemma=lemma
                , hidx= e['hidx']
                # , pos= e['pos'] # currently not used
                , type_entry=types[e['type_entry']]) 
        
        for g in e['genders']:
            entry_gender = Entry_Gender(entry=entry
                        , gender=genders[g])    
            entries_genders.append(entry_gender) 

        for s in e['spellings']:
            if s not in spellings:
                spellings[s] = Spelling(spelling=s)
            entry_spelling = Entry_Spelling(entry=entry, spelling=spellings[s])
            entries_spellings.append(entry_spelling)


        entries.append(entry)

    Entry.objects.bulk_create(entries)
    Spelling.objects.bulk_create(spellings.values())
    Entry_Gender.objects.bulk_create(entries_genders)
    Entry_Spelling.objects.bulk_create(entries_spellings)