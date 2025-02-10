from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

def articles_text(articles_list):
    """Return list of articles (der,die,das) as a string.
    
    Think about, whether it would be better if I resolve this by creating a order number in the Entry_Gender table at table creation...
    """
    # I need a list without repeated articles, but I cannot use set because I have to keep the order.
    # ...and I iterate over the list
    articles = []
    for article in articles_list:
        if article not in articles:
            articles.append(article)
    
    articles = [article.capitalize() for article in articles]
    return ', '.join(articles)


class Level(models.Model):
    """Goethe German Proficiency Levels"""
    level = models.CharField(max_length=2, null=False, unique=True)
    
    def __str__(self):
        return self.level
  
class Type_Entry(models.Model):
    type_name = models.CharField(max_length=30, null=False, unique=True)

    def __str__(self):
        return self.type_name

class Gender(models.Model):
    gender = models.CharField(max_length=10, null=False, unique=True)
    article = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.gender

class Spelling(models.Model):
    spelling = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        return self.spelling

# class Pos(models.Model):
#     pos_name = models.CharField(max_length=10, null=False, unique=True)

class Lemma(models.Model):
    lemma = models.CharField(max_length=100, null=False, unique=True)
    frequency = models.IntegerField(null=True)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def articles_text(self):
        """Return list of articles as a string.
        
        Lookup order: lemma -> entry (multiple) -> genders (multiple) -> article
        """
        articles = self.entry_set.all().order_by('hidx').values_list('genders__article', flat=True)
        return articles_text(articles)  
    
    @property
    def frequency_text(self):
        if self.frequency is None:
            return '-'
        return str(self.frequency)
           
    @property
    def level_text(self):
        if self.level is None:
            return "B2+"
        return str(self.level)
    
    def __str__(self):
        return self.lemma

class Entry(models.Model):
    lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE, null=False)
    hidx = models.IntegerField(null=True)
    type_entry = models.ForeignKey(Type_Entry, on_delete=models.SET_NULL, null=True, blank=True)
    # pos = models.CharField(max_length=10, null=True, blank=True)
    genders = models.ManyToManyField(Gender, through='Entry_Gender')
    spellings = models.ManyToManyField(Spelling, through='Entry_Spelling')


    @property
    def articles_text(self):
        """Return list of articles as a string.
        
        Lookup order:  entry  -> genders (multiple) -> article
        """
        articles =self.genders.values_list('article', flat=True)
        return articles_text(articles)

    @property
    def url_dwds(self):
        """Return DWDS url for the entry.
        
        comment: I could call the lemma text using self.lemma (because the string representation is the same) but the string representation might change, so I use self.lemma.lemma to avoid braking the code if the string representation changes.
        """
        if not self.hidx:
            url = f'https://www.dwds.de/wb/{self.lemma.lemma}'
        else:
            url = f'https://www.dwds.de/wb/{self.lemma.lemma}#{self.hidx}'    
        return url

    def __str__(self):
         if self.hidx is not None:
            return f'{self.lemma.lemma} ({self.hidx})'
         else:
            return self.lemma.lemma

class Entry_Gender(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, null=False)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.entry.lemma.lemma} ({self.gender})'

class Entry_Spelling(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, null=False)
    spelling = models.ForeignKey(Spelling, on_delete=models.SET_NULL, null=True, blank=True)
 

class Played(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    lemma = models.ForeignKey(Lemma, on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now_add=True)
    correct = models.BooleanField(null=False)

    def __str__(self):
        return f'{self.lemma.lemma}, {self.date}, {"correct" if self.correct else "wrong"}'

if __name__ == "__main__":
    pass
    # from dwds.entries import get_entries_nouns_df, get_sub_entries_df
    # entries = get_entries_nouns_df()
    # entries.type_entry.str.len().max() 
    # words = get_sub_entries_df()
    # words.lemma.str.len().max()
    # words.pos_entry.str.len().max()
 