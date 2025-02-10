import django_tables2 as tables
from django.utils.html import format_html
from .models import Entry, Lemma # type: ignore
from django.db.models import F
from django.urls import reverse

class HistoryTable(tables.Table):
    count = tables.Column(verbose_name="Words")
    correct_count = tables.Column(  verbose_name="Correct")
    correct_pct = tables.Column( empty_values=(), verbose_name=" % " )

    class Meta:
        orderable = False
        attrs = {
                    'class': "table table-sm table-info table-hover",
                }

    def render_correct_pct(self,value):
        return f'{value:.0f} %'

class HistoryTableDetail(HistoryTable, tables.Table):
    """Shown in the user's history by words page"""
    lemma = tables.Column(empty_values=(), verbose_name=" ")
    class Meta:
        attrs = {
                'class': "table table-sm table-info table-hover",
                }
    
    def render_lemma(self,record, value):
        lemma_obj = Lemma.objects.get(id=value)
        return format_html(f'<a href="{reverse("der_die_das:lemma", args=[value])}" target="_blank">{lemma_obj.articles_text} {lemma_obj.lemma}</a>')
     
class EntryListTable(tables.Table):
    class Meta:
         model = Entry
         fields = ()
         orderable = True
        #  order_by = ('level' )  
         attrs = {
                    'class': 'table table-hover',
                    'thead': {
                        'class': 'table-light', #  'table-primary', 
                    },
                }
          
    entry = tables.Column( empty_values=(), verbose_name="Word")
    genders = tables.Column(empty_values=(), verbose_name="Articles")
    level = tables.Column(empty_values=(), verbose_name="Level")
    frequency = tables.Column(empty_values=(), verbose_name="Freq.")
    url = tables.Column(empty_values=(), verbose_name="DWDS")
   
    def render_entry(self,record):
        if record.hidx is not None:
            entry = f'{record.lemma.lemma} ({record.hidx})'
        else:
            entry = f'{record.lemma.lemma}'
        return format_html(f'<strong>{record.articles_text}</strong> {entry}')
    
    def order_entry(self, queryset, is_descending):
        queryset = queryset.order_by(("-" if is_descending else "") + "lemma__lemma", "hidx")
        return (queryset, True)     
        
    def render_genders(self,record):
        return f"{ record.articles_text}"

    def render_level(self,record):
        return f"{ record.lemma.level_text}"
    
    def order_level(self, queryset, is_descending):
        if is_descending:
            queryset = queryset.order_by(F('lemma__level').desc(nulls_last=True))
        else:
            queryset = queryset.order_by(F('lemma__level').asc(nulls_last=True))
        return (queryset, True)   

    def render_frequency(self,record):
        return f"{record.lemma.frequency_text}"
    
    def order_frequency(self, queryset, is_descending):
        if is_descending:
            queryset = queryset.order_by(F('lemma__frequency').desc(nulls_last=True))
        else:
            queryset = queryset.order_by(F('lemma__frequency').asc(nulls_last=True))
        return (queryset, True)

    def render_url(self,record):
        return format_html(f'<a href="{record.url_dwds}" target="_blank" class="btn btn-primary btn-sm">go to DWDS</a>')
    
    
class EntryListTableSmall(EntryListTable):
    """Shown in the search for word on the navbar"""
    entry = tables.Column( empty_values=(), verbose_name="Word")
    genders = None
    level =  None
    frequency = None
    url = tables.Column(empty_values=(), verbose_name="DWDS")
 
    