import folium

def get_map(forecast):
    # Get weather data for the selected location
    weather_data = forecast[0]  # assuming forecast is a list of weather data for multiple days

    # Get latitude and longitude for the selected location
    lat = weather_data['latitude']
    lon = weather_data['longitude']

    # Create a folium map centered on the selected location
    map = folium.Map(location=[lat, lon], zoom_start=10)

    # Add weather data overlays to the map
    tooltip = f"{weather_data['city']}, {weather_data['state']}, {weather_data['country']}"
    folium.Marker(location=[lat, lon], tooltip=tooltip).add_to(map)
    folium.Marker(location=[lat, lon], tooltip=tooltip).add_to(map)
    folium.TileLayer('openweathermap', attr='OpenWeatherMap').add_to(map)
    folium.TileLayer('openstreetmap', attr='OpenStreetMap').add_to(map)
    folium.LayerControl().add_to(map)

    return map._repr_html_()
