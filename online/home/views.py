from django.shortcuts import render, redirect
from django.views import View
from der_die_das.forms import ByLemmaForm # type: ignore
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.contrib import messages

class Index(View):
    def get(self, request):
        form = ByLemmaForm()
        return render(request, 'home/index.html', {'form': form})


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # log in user after creating it!
            login(request,user)
            return redirect('home:index')
    else:
        form = UserCreationForm()
    context = {'form':form}
    return render(request, "registration/register.html", context)


class DeregisterView(LoginRequiredMixin, View):
    def get(self, request):
        """landing page from login asking user if they are sure they want to deregister"""
        return render(request, "registration/deregister.html")

    def post(self, request):
        request.user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("home:index")
