from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.db.models import Count, Q, Sum,  ExpressionWrapper, FloatField, IntegerField, F
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib import messages
 
from django_tables2 import RequestConfig
import django_tables2 as tables2

from .forms import  EntryListForm, GameSetupForm
from .models import Lemma, Entry, Gender, Level, Played 
from .tables import EntryListTable, HistoryTable, EntryListTableSmall, HistoryTableDetail

from my_decorators import timer
from .constants import ALL_ENTRIES, GENDERS, LEMMATA_LEVELS, LEMMATA_ID_LEVELS, LEMMATA_LEN_LEVELS,LEVELS_MAP, ARTICLES_MAP

import random


def lemmata_by_lemma_or_spelling(lemma_text): 
    # lemma__iexact
    """Return lemma objects by lemma text or spelling."""
    lemma = Lemma.objects.select_related().filter(lemma__iexact=lemma_text) 
    if not lemma:
        lemma = Lemma.objects.select_related().filter(entry__spellings__spelling=lemma_text).distinct() 
    if not lemma:
        lemma = []
    return lemma # already evaluated 

@timer
def entries_by_lemma_wildcard(search):
    """Return entries whose lemma contains, starts with or ends with a given search string."""
    if not search:
        entries = ALL_ENTRIES
        return entries

    if not '*'  in search:
        entries = Entry.objects.select_related().filter(lemma__lemma=search)
        return entries

    to_search = search.replace('*', '')
    if search.startswith('*') and search.endswith('*'):
        entries = Entry.objects.select_related().filter(lemma__lemma__contains=to_search)

    elif search.startswith('*'):
        entries = Entry.objects.select_related().filter(lemma__lemma__endswith=to_search)

    elif search.endswith('*'):
        entries = Entry.objects.select_related().filter(lemma__lemma__startswith=to_search)
    
    return entries


@timer
def entries_by_article(entries):
    """Entries by article in a dictionary."""
    dic = { f'{id}': entries.filter(genders=id) for id, _ in GENDERS}
    dic['0'] = entries
    return dic

def get_count_lemma_data(lemma):
    data  = lemma.entry_set.all().aggregate(entries_count = Count('id', distinct=True), lemma_genders_count=Count('genders', distinct=True))
    return data


@timer
def get_count_entries_data(entries):
    """Return aggregate values over all entries.
    
    Counts of words (entries), 
    Counts of total articles/genders (der,die,das) - a word can have more than one article
    Counts of words per article  
    """
    aggregate = dict()
    aggregate['articles_count'] = Count('genders')
    aggregate['words_count'] = Count('id', distinct=True)
    for id, _ in GENDERS: # count by article/gender
        filter = Q(genders  = id)
        aggregate[f'{id}'] =  Count('genders', filter = filter)

    counts = entries.values_list('genders').aggregate(**aggregate)
    counts = {ARTICLES_MAP.get(key, key):value for key, value in counts.items()} 
    return counts

@timer
def get_count_chart_data(counts):
    """Format data for google chart."""
    counts_chart = [[key, value] for key, value in counts.items() if not 'count' in key]
    counts_chart.insert(0, ['article', 'count'])
    return counts_chart

def lemmata_search_list(request,lemmata):
    context = {'lemmata': lemmata}
    return render(request, 'der_die_das/lemma_search_list.html', context)


class LemmaView(DetailView):
    """View for a single lemma."""
    model = Lemma 
    template_name = 'der_die_das/lemma_detail.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        lemma = context['lemma']
        entries = lemma.entry_set.all().order_by('hidx')
        context.update(get_count_lemma_data(lemma))
        context['entries'] = entries
        context['table'] = EntryListTableSmall(entries)
        return context
    

class LemmaSearchView(View):
    def get(self, request):
        print('print REQUEST.GET:', request.GET)

        if (search := request.GET.get('search')):
            next = request.GET.get('next', 'home:index' )
            search = search.strip()
            search = search[:1].upper() + search[1:] # Capitalize only first letter
            lemmata = lemmata_by_lemma_or_spelling(search)
            # print(f'{lemma = }')
            if len(lemmata)== 1:
                return redirect(reverse('der_die_das:lemma',args=(lemmata[0].id,)))
            elif len(lemmata) > 1:
                return lemmata_search_list(request,lemmata)
            else:
                messages.add_message(request, messages.WARNING, f"<p>The word <strong>{search}</strong> was not found, try again!</p>")
                return redirect(next)

    
class EntryList(View):
    """list of entries, providing info on genders, frequency, level, and DWDS urls"""
    @timer
    def get(self, request):
        print('print REQUEST.GET:', request.GET)
  
        search = request.GET.get('search') 
        levels = request.GET.getlist('level')
        frequencies = request.GET.getlist('frequency')
        what = request.GET.get('what')
        chart = True if str(request.GET.get('what')) == 'Chart' else False
        context = dict()
        if what is None:
                what = 'Chart'  # populate with chart by default
                chart = True

        form = EntryListForm(request.GET)

        search = search.strip() if search else ''
        entries = entries_by_lemma_wildcard(search)
        if levels:
            entries = entries.filter(lemma__level__in=levels)
        if frequencies:
            entries = entries.filter(lemma__frequency__in=frequencies)
        
        # order did not work through tables2
        entries = entries.order_by(F('lemma__level').asc(nulls_last=True), 'lemma__lemma',  'hidx')
        # filters in text as a dict
        filters = dict(Search = search, Levels=levels, Frequencies=frequencies)
        filters['Levels'] = ', '.join(LEVELS_MAP[level] for level in levels) 
        filters['Frequencies'] = ', '.join(frequencies)
        filters = {key: value for key, value in filters.items() if value}
        context['filters'] = filters
        # summary data (label and count)
        count_data = get_count_entries_data(entries)
        context['counts'] = {key.replace('_count', ' ').title(): f'{value:,}' 
                             for key, value in count_data.items() }
 
        # summary data only articles for chart
        context['counts_chart'] =  get_count_chart_data(count_data)
        context['entries_exist'] =  True if entries.exists() else False

        if not entries.exists():
            messages.add_message(request, messages.WARNING, f"<p>No words found for your search. Try adjusting your filters and search again!</p>")

        if not chart:
            # entries by article (gender)
            entries_dict = entries_by_article(entries)
            # entries into tables2
            table = EntryListTable(entries_dict[what])
            # set pagination
            RequestConfig(request, paginate={"per_page": 25}).configure(table)
            context['data_table'] =  table

        first_upper = lambda s: s[:1].upper() + s[1:]  
        context['articles'] = [('0', 'All')] + [(id, first_upper(article)) for id, article in ARTICLES_MAP.items()]
        context['form'] = form    
 
        context.update({'what' : what, 'chart' : chart})
        return render(request, 'der_die_das/entry_list.html', context)
    
    
def style_correct(correct):
    """return style for correct and incorrect answers, where correct is boolean"""
    if correct:
        return "background-color:#ff2a2a; color:white;" # 
    else:
        return  "background-color:#00c3b6;"

def reset_game(request):
    request.session['score'] = 0
    request.session['rounds'] = 0
    request.session['message'] = ''
    request.session['last_lemma_id'] = None
    request.session['style'] = style_correct(True)
    # if the user visits the game for the first time, or session expired, level will not be set
    # then set default level to 1 (A1)
    level_id = request.GET.get('level') if request.GET.get('level') else '1'
    request.session['level_id'] = level_id  
    request.session['level_label'] = LEVELS_MAP[level_id]

    # select set of words
    lemmata = list(LEMMATA_ID_LEVELS[int(level_id)])
    # add some randomness
    random.shuffle(lemmata)
    request.session['lemmata'] = lemmata[:100]

class Game(View):
    @timer
    def get(self, request):
        print('print REQUEST.GET:', list(request.GET.items()))
        print('print SESSION:', request.session.items())

        # change of the level/reset requested
        if  request.GET.get('Reset') == 'Reset':
            reset_game(request)
            print('New Game')
            return redirect(reverse('der_die_das:game'))
        else:
            # first time visiting the game
            if not request.session.get('level_id'):
                print('First time visiting the game')
                reset_game(request)
                
        context = dict()        
        if lemmata:=request.session['lemmata']:
            lemma_id = lemmata[0]
            lemma = Lemma.objects.get(id=lemma_id)
            lemma_articles = lemma.entry_set.values_list('genders__article', flat = True).distinct()
            answers = dict()
            for _ , article in GENDERS:
                answers[article] = True if article in lemma_articles else False
            context['answers'] = answers
            request.session["lemma_id"] = lemma.id

        # game over
        else:
            lemma = None

        if last_lemma := request.session.get('last_lemma_id'):
            last_lemma =  Lemma.objects.get(id=last_lemma)
            context['last_lemma'] = f'{last_lemma.articles_text} {last_lemma}'
            
        context['lemma'] = lemma
        form = GameSetupForm({'level':request.session['level_id']})
        context['form'] = form

        return render(request, 'der_die_das/game.html', context) 

    @timer
    def post(self, request):
        """This handles the answer of the questions and updates counters"""
        # print('print REQUEST.POST:', request.POST)

        score = request.session.get('score')
        correct = request.POST.get('correct') == 'True'
        # replace last round lemma
        last_lemma_id = request.session.get('lemma_id')
        request.session['last_lemma_id'] = last_lemma_id
        
        # update counters
        request.session['score'] = score + 1 if correct else score
        request.session['rounds'] = request.session.get('rounds', 0)  + 1  

        # message to be used in next get
        request.session['message'] = '&#9734;' if correct else '&#10008;' # ☆ &#9734; ✘ &#10008;
        request.session['style'] = style_correct(correct)

        # update lemmata list, if wrong insert at random position 
        lemmata = request.session.get('lemmata')
        if correct:
            lemmata = lemmata[1:]
        if not correct:
            lemmata = lemmata + [last_lemma_id] 
            random.shuffle(lemmata)
        
        request.session['lemmata'] = lemmata
        
        # save round to database
        if request.user.is_authenticated:
            last_lemma = Lemma.objects.get(id=last_lemma_id)
            played = Played(user=request.user, 
                            lemma=last_lemma,
                            correct=correct)
            played.save()

        return redirect(request.path) 
    

def history_by_user(user):
    from django.db.models.functions import TruncDay

    def annotate(query):
        q = (query
                .annotate(count=Count('id'))
                .annotate(correct_count=ExpressionWrapper(Sum('correct'),output_field=IntegerField() ))
                .annotate(correct_pct=ExpressionWrapper(F('correct_count') *100.0 / F('count'), output_field=FloatField()))
                .annotate(wrong=ExpressionWrapper(F('count')-F('correct_count'), output_field=IntegerField())))
        return q

    user_rows = Played.objects.filter(user= user) 

    data = dict()
    data['total'] = annotate(user_rows.values('user', 'user__username'))
    data['by_level'] = annotate(user_rows.values('lemma__level__level'))
    data['by_day'] = annotate(user_rows.annotate(day = TruncDay('date')).values('day'))
    data['by_lemma'] = annotate(user_rows.values('lemma'))

    summary_tables = ['total', 'by_level', 'by_day']
    extra = dict()
    extra['total'] = None
    extra['by_level'] = [('lemma__level__level', tables2.Column(verbose_name="Level"))]
    extra['by_day'] = [('day', tables2.DateTimeColumn(verbose_name="Day", format=r'D d\, M Y')), ]
     
    tables = {key: HistoryTable(data, extra_columns=extra.get(key)) for key, data in data.items() if key in summary_tables}

    # special table for details
    tables['by_lemma'] = HistoryTableDetail(data['by_lemma'])

    tables['by_level'].sequence = ['lemma__level__level', '...']
    tables['by_day'].sequence = ['day', '...']
    tables['by_lemma'].sequence = ['lemma', '...']
    return tables

class History(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        user_rows = Played.objects.filter(user= user) 
        context = dict(is_history=False)
        if not user_rows:
            print('No games saved')
        
        else:
            context['is_history'] = True
            data = history_by_user(user)
            # the following was required to allow sorting tables on the page
            data = {key:RequestConfig(request).configure(data) for key, data in data.items()}
            RequestConfig(request).configure(data['by_lemma'])
            context.update(data)
            if request.GET.get('detail'):
                return render(request, 'der_die_das/history_detail.html', context=context)
                
        return render(request, 'der_die_das/history.html', context=context)
        
 
class DeleteHistory(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        user_rows = Played.objects.filter(user= user)
    
        if user_rows:
             user_rows.delete()
                     
        return redirect(reverse('der_die_das:history'))
    


    
