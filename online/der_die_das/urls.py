from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = "der_die_das"
urlpatterns = [
    path("lemma/", views.LemmaSearchView.as_view(), name="lemmataSearch"),
    path("lemma/<int:pk>", views.LemmaView.as_view(), name="lemma"),
    path("entries/", views.EntryList.as_view(), name="entryList"),
    path("history/", views.History.as_view(), name="history"),
    path("game/", views.Game.as_view(), name="game"),
    path('delete/', views.DeleteHistory.as_view(), name = 'delete_history' ),

]
