import requests
from django.conf import settings
from django.core.cache import cache

def get_forecast(city, state, country):
    api_key = settings.API_KEY # replace with your OpenWeatherMap API key
    base_url = 'http://api.openweathermap.org/data/2.5/forecast'
    params = {
        'q': f'{city},{state},{country}',
        'units': 'metric',
        'cnt': 5,  # specify number of days to forecast
        'appid': api_key
    }

    # Try to get the forecast from cache first
    cache_key = f"forecast-{city}-{state}-{country}"
    forecast = cache.get(cache_key)

    if forecast is None:
        # If the forecast is not in cache, fetch it from the API and cache it
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            forecast = []
            for i in range(params['cnt']):
                weather = {
                    'date': data['list'][i]['dt_txt'],
                    'city':city,
                    'state':state,
                    'country':country,
                    'temperature': data['list'][i]['main']['temp'],
                    'humidity': data['list'][i]['main']['humidity'],
                    'wind_speed': data['list'][i]['wind']['speed'],
                    'description': data['list'][i]['weather'][0]['description'],     
                    'longitude': data['city']['coord']['lon'],
                    'latitude': data['city']['coord']['lat'],
                    'uv_index': get_uv_index(data['city']['coord']['lon'],data['city']['coord']['lat']),
                    'air_quality': get_air_quality(data['city']['coord']['lon'],data['city']['coord']['lat']),
                }
                forecast.append(weather)
            cache.set(cache_key, forecast, timeout=600)  # cache for 10 minutes (600 seconds)
        else:
            return None
    return forecast


def get_uv_index(latitude, longitude):
    api_key = settings.API_KEY # replace with your OpenUV API key
    base_url = 'https://api.openuv.io/api/v1/uv'
    params = {
        'lat': latitude,
        'lng': longitude
    }
    headers = {
        'x-access-token': api_key
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['result']['uv']
    else:
        return None

def get_air_quality(latitude, longitude):
    api_key = settings.API_KEY # replace with your OpenWeatherMap API key
    base_url = 'http://api.openweathermap.org/data/2.5/air_pollution'
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['list'][0]['main']['aqi']
    else:
        return None