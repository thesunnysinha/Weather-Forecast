import logging
import requests
from django.conf import settings
from django.core.cache import cache

# Configure logging
logger = logging.getLogger(__name__)

def get_forecast(city, state, country):
    """
    Fetches a 5-day weather forecast from OpenWeatherMap API.
    Tries to retrieve data from cache first; otherwise, fetches from API and caches it.
    """
    api_key = settings.API_KEY  # Ensure this is set in Django settings
    base_url = 'http://api.openweathermap.org/data/2.5/forecast'
    
    params = {
        'q': f'{city},{state},{country}',
        'units': 'metric',
        'cnt': 5,  # Forecast for 5 time slots
        'appid': api_key
    }

    cache_key = f"forecast-{city}-{state}-{country}"
    forecast = cache.get(cache_key)

    if forecast:
        logger.info(f"Cache hit for forecast: {city}, {state}, {country}")
        return forecast

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # Raises an error for non-200 status codes

        data = response.json()
        if 'list' not in data or 'city' not in data:
            logger.error(f"Unexpected API response for {city}, {state}, {country}: {data}")
            return None

        forecast = []
        longitude, latitude = data['city']['coord']['lon'], data['city']['coord']['lat']

        for i in range(params['cnt']):
            weather_data = data['list'][i]
            weather = {
                'date': weather_data['dt_txt'],
                'city': city,
                'state': state,
                'country': country,
                'temperature': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'wind_speed': weather_data['wind']['speed'],
                'description': weather_data['weather'][0]['description'],
                'longitude': longitude,
                'latitude': latitude,
                'uv_index': get_uv_index(latitude, longitude),
                'air_quality': get_air_quality(latitude, longitude),
            }
            forecast.append(weather)

        # Cache the forecast for 10 minutes
        cache.set(cache_key, forecast, timeout=600)
        logger.info(f"Fetched forecast from API and cached: {city}, {state}, {country}")

        return forecast

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch forecast for {city}, {state}, {country}: {e}")
        return None


def get_uv_index(latitude, longitude):
    """
    Fetches the UV index from OpenUV API. Caches the response for 1 hour.
    """
    api_key = settings.API_KEY  # Ensure this is set in Django settings
    base_url = 'https://api.openuv.io/api/v1/uv'
    
    cache_key = f"uv-index-{latitude}-{longitude}"
    cached_uv = cache.get(cache_key)
    if cached_uv:
        logger.info(f"Cache hit for UV index: {latitude}, {longitude}")
        return cached_uv

    try:
        headers = {'x-access-token': api_key}
        params = {'lat': latitude, 'lng': longitude}
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        uv_index = data.get('result', {}).get('uv')

        if uv_index is not None:
            cache.set(cache_key, uv_index, timeout=3600)  # Cache for 1 hour
            logger.info(f"Fetched UV index from API: {latitude}, {longitude} -> {uv_index}")
        else:
            logger.warning(f"UV index not found in response: {data}")

        return uv_index

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch UV index for {latitude}, {longitude}: {e}")
        return None


def get_air_quality(latitude, longitude):
    """
    Fetches the air quality index (AQI) from OpenWeatherMap API. Caches the response for 1 hour.
    """
    api_key = settings.API_KEY  # Ensure this is set in Django settings
    base_url = 'http://api.openweathermap.org/data/2.5/air_pollution'
    
    cache_key = f"air-quality-{latitude}-{longitude}"
    cached_aqi = cache.get(cache_key)
    if cached_aqi:
        logger.info(f"Cache hit for air quality: {latitude}, {longitude}")
        return cached_aqi

    try:
        params = {'lat': latitude, 'lon': longitude, 'appid': api_key}
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        aqi = data.get('list', [{}])[0].get('main', {}).get('aqi')

        if aqi is not None:
            cache.set(cache_key, aqi, timeout=3600)  # Cache for 1 hour
            logger.info(f"Fetched air quality from API: {latitude}, {longitude} -> {aqi}")
        else:
            logger.warning(f"Air quality index not found in response: {data}")

        return aqi

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch air quality for {latitude}, {longitude}: {e}")
        return None
