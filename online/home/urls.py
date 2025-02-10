from django.urls import path
from . import views  
from django.views.generic import TemplateView

app_name = "home"
urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path('register/', views.register_view, name="register"),
    path('deregister/', views.DeregisterView.as_view(), name="deregister"),
    path('settings/', TemplateView.as_view(template_name = 'registration/settings.html'), name = 'settings' ),
]