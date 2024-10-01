from django.shortcuts import render
import requests
import os
from datetime import datetime
def get_weather_data(city):
    Api_key = str(os.getenv('API_KEY'))
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
    weather = None
    weather_description = None
    city_name = city
    country = 'CR'
    wind_speed = ''
    pressure = ''
    humidity = '0'
    temperature = ""
    if city:
        weather_data_result = get_weather_data(city)
        if weather_data_result is not None:
            icon_id = weather_data_result['weather'][0]['icon']
            icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
            weather = weather_data_result['weather'][0]['main']
            weather_description = weather_data_result['weather'][0]['description']
            city_name = weather_data_result['name']
            country = weather_data_result['sys']['country']
            wind_speed = weather_data_result['wind']['speed']
            pressure = weather_data_result['main']['pressure']
            humidity = weather_data_result['main']['humidity']
            temperature = round(weather_data_result['main']['temp'])
        else:
            
            return render(request,'core/index.html')
        

    return render(request, 'core/index.html',{
        'icon_url':icon_url,
        'weather': weather,
        'weather_description': weather_description,
        'city':city_name,
        'country':country,
        'wind_speed': wind_speed,
        'pressure' : pressure,
        'humidity': humidity,
        'temperature': temperature,
    })

def hourly(city):
    Api_key = str(os.getenv('API_KEY'))
    #Api_key = "2b460c2135a2d363006e86ad30592fdf"
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

def daily(city):
    Api_key = str(os.getenv('API_KEY'))
    
    base_url = f"https://api.openweathermap.org/data/2.5/forecast"
    parameters = {
        'q' : city,
        'appid' : Api_key,
        'units' : 'metric',
    }
    try:
        response = requests.get(base_url,params=parameters)
        if response.status_code == 200:
            data = response.json()
            
            daily_forecast = {}
            for entry in data['list']:
                date = datetime.fromtimestamp(entry['dt']).strftime('%Y-%m-%d')
                if date not in daily_forecast:
                    daily_forecast[date] = {
                        'date': date,
                        'icon': entry['weather'][0]['icon'],
                        'feels like': entry['main']['feels_like'],
                        'temp_min': entry['main']['temp_min'],
                        'temp_max': entry['main']['temp_max'],
                        'temp': entry['main']['temp'],
                    }
                else:
                    daily_forecast[date]['temp_min'] = min(daily_forecast[date]['temp_min'], entry['main']['temp_min'])
                    daily_forecast[date]['temp_max'] = max(daily_forecast[date]['temp_max'], entry['main']['temp_max'])

            daily_forecast_list = list(daily_forecast.values())
            daily_forecast_list.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
            return daily_forecast_list
        else: 
            return None
    except requests.exceptions.RequestException as e:
        response = None

    

def detail(request,city):

    forecast = daily(city)
    weather_data_result = get_weather_data(city)
    hours = hourly(city)
    if weather_data_result and forecast:
        city = weather_data_result['name']
        weather = weather_data_result['weather'][0]['main']
        temperature = round(weather_data_result['main']['temp'])
        temp_max = round(weather_data_result['main']['temp_max'])
        temp_min = round(weather_data_result['main']['temp_min'])
        # Get forecast data from json
        forecast_data = []
        for day in forecast:
            if (round(day['temp_max']) - round(day['temp_min'])) == 0:
                bar = 5
            else:
                bar = ((round(day['temp_max']) - round(day['temp'])) / (round(day['temp_max']) - round(day['temp_min']))) * 5
            result = round(bar)
            print(result)
            day_weather = {
                'date': datetime.strptime(day['date'], '%Y-%m-%d').strftime('%A'),
                'icon':f"https://openweathermap.org/img/wn/{day['icon']}@2x.png",
                'temp_min': round(day['temp_min'],),
                'temp_max': round(day['temp_max']),
                'feels_like': round(day['feels like']),
                'bar': result,
            }
            forecast_data.append(day_weather)
    else:
        return render(request, 'core/detail.html')

    if hours:
        hourly_forecast = []
        for hour in hours['list']:
            hourly_forecast.append({
                'time': datetime.fromtimestamp(hour['dt']).strftime('%Y-%m-%d'),
                'icon':f"https://openweathermap.org/img/wn/{hour['weather'][0]['icon']}@2x.png",
                'temperature': round(hour['main']['temp']),
                'dt_time': datetime.strptime(hour['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%I%p').lstrip('0')
            })

        hourly_forecast.sort(key=lambda x: x['time'])
        hourly_forecast = hourly_forecast[:15]
        current = datetime.strptime(hourly_forecast[0]['time'], '%Y-%m-%d').strftime('%A, %B %d, %Y')
    return render(request,'core/detail.html', {
        'hourly_forecast':hourly_forecast,
        'city':city,
        'current':current,
        'weather':weather,
        'temperature':temperature,
        'forecast':forecast_data,
        'temp_max':temp_max,
        'temp_min':temp_min
        })


