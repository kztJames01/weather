from django.shortcuts import render
import requests
import json
from datetime import datetime
def get_weather_data(city):
    Api_key = "d58c475f4f008441996e9bb1a2343ed3"
    base_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={Api_key}"
    parameters = {
        'q' : city,
        'appid' : Api_key,
        'exclude' : 'minutely,hourly',
        'units' : 'metric',
    }
    try:
        response = requests.get(base_url,params=parameters)
        if response.status_code == 200:
            
            return response.json()
        else: 
            return None
    except requests.exceptions.RequestException as e:
        response = None
    

def index(request):
    city = request.GET.get('city')
    icon_url = 'https://openweathermap.org/img/wn/10d@2x.png'
    if city:
        weather_data_result = get_weather_data(city)
        if weather_data_result is not None:
            weather_data = json.dumps(weather_data_result,indent=4)
            print(weather_data)
            icon_id = weather_data_result['weather'][0]['icon']
            icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"

            weather = weather_data_result['weather'][0]['main']
            weather_description = weather_data_result['weather'][0]['description']
            city = weather_data_result['name']
            country = weather_data_result['sys']['country']
            wind_speed = weather_data_result['wind']['speed']
            pressure = weather_data_result['main']['pressure']
            humidity = weather_data_result['main']['humidity']
            temperature = weather_data_result['main']['temp']
        else:
            
            return render(request,'core/index.html')
        

    return render(request, 'core/index.html',{
        'icon_url':icon_url,
        'weather': weather,
        'weather_description': weather_description,
        'city':city,
        'country':country,
        'wind_speed': wind_speed,
        'pressure' : pressure,
        'humidity': humidity,
        'temperature': temperature,
    })
def daily(city):
    #Api_key = "d58c475f4f008441996e9bb1a2343ed3"
    cnt = 7
    Api_key = "2b460c2135a2d363006e86ad30592fdf"
    base_url = f"https://api.openweathermap.org/data/2.5/forecast"
    parameters = {
        'q' : city,
        'appid' : Api_key,
        'units' : 'metric',
    }
    try:
        response = requests.get(base_url,params=parameters)
        if response.status_code == 200:
            return response.json()
        else: 
            return None
    except requests.exceptions.RequestException as e:
        response = None

def detail(request,city):
    forecast = daily(city)
    weather_data_result = get_weather_data(city)
    
    if weather_data_result:
        city = weather_data_result['name']
        weather = weather_data_result['weather'][0]['main']
        temperature = weather_data_result['main']['temp']
        forecast_data = []
        for day in forecast['list']:
            date = datetime.fromtimestamp(day['dt']).strftime('%A')
            icon_id = day['weather'][0]['icon']
            icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
            day_weather = {
                'date': date,
                'icon': icon_url,
                'temp_min': day['main']['temp_min'],
                'temp_max': day['main']['temp_max']
            }
            forecast_data.append(day_weather)
    else:
        return render(request, 'core/detail.html')
    return render(request,'core/detail.html', {
        'city':city,
        'weather':weather,
        'temperature':temperature,
        'forecast':forecast_data,
        })


