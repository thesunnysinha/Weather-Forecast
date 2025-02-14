import logging
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .forms import LocationForm, SignUpForm
from .models import FavoriteLocation
from .utils import get_forecast
from .maps import get_map

# Configure logging
logger = logging.getLogger(__name__)

def locations(request):
    """
    Handles location search, adding to favorites, and sending emails.
    """
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            country = form.cleaned_data['country']
            action = request.POST.get('action')

            # Handle different actions
            if action == 'search':
                logger.info(f"User {request.user} searched for location: {city}, {state}, {country}")
                forecast = get_forecast(city, state, country)
                location_map = get_map(forecast)
                return render(request, 'location_search.html', {
                    'data': form.cleaned_data,
                    'forecast': forecast,
                    'form': form,
                    'location_map': location_map
                })

            elif action == 'add-to-favorites':
                if request.user.is_authenticated:
                    # Use `get_or_create` to avoid redundant queries
                    favorite_location, created = FavoriteLocation.objects.get_or_create(
                        user=request.user, city=city, state=state, country=country
                    )
                    if created:
                        messages.success(request, f"{city}, {state}, {country} added to favorites")
                        logger.info(f"User {request.user} added {city}, {state}, {country} to favorites")
                    else:
                        messages.warning(request, f"{city}, {state}, {country} is already in favorites")
                    return redirect('profile')
                else:
                    messages.error(request, "You need to log in to add favorites")
                    return redirect('login')

            elif action == 'send-mail':
                if request.user.is_authenticated:
                    email_to = request.POST.get('email')
                    subject = 'Weather Forecast'
                    message = render_to_string('forecast.html', {'forecast': get_forecast(city, state, country)})
                    msg = EmailMessage(subject, message, to=[email_to], from_email=settings.DEFAULT_FROM_EMAIL)
                    msg.content_subtype = 'html'
                    msg.send()
                    messages.success(request, "Mail sent successfully! Check your inbox.")
                    logger.info(f"User {request.user} sent weather forecast email to {email_to}")
                else:
                    messages.error(request, "You need to log in to send emails")
                    return redirect('login')

    else:
        # Render an empty form initially
        form = LocationForm()
    
    return render(request, 'location_search.html', {'form': form})


@login_required
def profile(request):
    """
    Displays the user's favorite locations.
    """
    user_locations = FavoriteLocation.objects.filter(user=request.user)
    logger.info(f"User {request.user} accessed their profile page.")
    return render(request, 'profile.html', {"locations": user_locations})


def login(request):
    """
    Handles user authentication and login.
    """
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            auth_login(request, user)
            logger.info(f"User {username} logged in successfully.")
            return redirect('home')
        else:
            messages.error(request, 'Incorrect username or password!')
            logger.warning(f"Failed login attempt for username: {username}")

    return render(request, 'login.html')


def signup(request):
    """
    Handles user registration.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():  # Added missing parentheses
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')  # Get the password to authenticate user

            user = authenticate(username=username, password=password)
            if user:
                auth_login(request, user)
                messages.success(request, f'Congratulations {username}! Signup successful.')
                logger.info(f"New user {username} signed up and logged in.")
                return redirect('profile')

    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})


@login_required
def logout(request):
    """
    Logs out the user and redirects to the login page.
    """
    logger.info(f"User {request.user} logged out.")
    auth_logout(request)
    return redirect('login')
