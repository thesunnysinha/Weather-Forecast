from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, TemplateView,View
from .forms import LocationForm,SignUpForm
from .models import FavoriteLocation
from .utils import get_forecast
from .maps import get_map
from django.shortcuts import redirect,render
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect

def locations(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']
            if 'action' in request.POST:
                if request.POST['action'] == 'search':
                    forecast = get_forecast(city, state, country)
                    location_map = get_map(forecast)
                    data = form.cleaned_data
                    return render(request, 'location_search.html', {'data': data, 'forecast': forecast, 'form': form,'location_map':location_map})
                elif request.POST['action'] == 'add-to-favorites':
                    if request.user.is_authenticated:
                        existing_location = FavoriteLocation.objects.filter(user=request.user, city=city, state=state, country=country).exists()
                        if existing_location:
                            messages.warning(request, f"{city}, {state}, {country} already in favorites ")
                        else:
                            favorite_location = FavoriteLocation.objects.create(user=request.user, city=city, state=state, country=country)
                            messages.success(request, f"{city}, {state}, {country} added to favorites ")
                        return render(request, 'location_search.html', {'form': form})
                    else:
                        return redirect('login')
                elif request.POST['action'] == 'send-mail':
                    if request.user.is_authenticated:
                        subject = 'Weather Forecast'
                        to = [request.POST['email']]
                        from_email = settings.DEFAULT_FROM_EMAIL

                        message = render_to_string('forecast.html', {'forecast': forecast})

                        msg = EmailMessage(subject, message, to=to, from_email=from_email)
                        msg.content_subtype = 'html'
                        msg.send()
                        messages.success("Mail Sent Successfully,Check Your Mailbox")
                    else:
                        return redirect('login')              
    else:
        # Render initial form
        form = LocationForm()
    return render(request, 'location_search.html', {'form': form})


@login_required
def profile(request):
    user_locations = FavoriteLocation.objects.filter(user=request.user)
    return render(request, 'profile.html',{"locations":user_locations})


def login(request):
    if request.method == "POST":
        username= request.POST.get('username')
        password= request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')

        else:
            messages.info(request, 'Username or password is incorrent !')
    context = {}
    return render(request,'login.html',context)


def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid:
            form.save()
            user = authenticate(username = username,password= password)
            auth_login(request,user)
            name = form.cleaned_data.get('username')
            messages.success(request, 'Congratulations! '+ name +'. SignUp Successfull')
            return redirect('profile')
    else:
        form = SignUpForm()
    context ={'form':form}
    return render(request,'signup.html',context)


@login_required
def logout(request):
    auth_logout(request)
    return redirect('login')

