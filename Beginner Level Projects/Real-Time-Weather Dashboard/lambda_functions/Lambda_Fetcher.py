import json
import boto3
import urllib3
import time
from datetime import datetime, timedelta
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('WeatherData')
http = urllib3.PoolManager()

def get_peru_time():
    return datetime.utcnow() - timedelta(hours=5)

def lambda_handler(event, context):
    API_KEY = os.environ.get('OPEN_WEATHER_KEY')
    CITY = "Lima"
    
    if not API_KEY:
        return {
            'statusCode': 500,
            'body': json.dumps('Error: API_KEY no configurada')
        }
    
    try:
        # 1. GEOCODING - CAMBIADO LIMIT=1
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={CITY}&limit=1&APPID={API_KEY}"
        print(f"Calling geo URL: {geo_url}")
        
        geo_response = http.request('GET', geo_url)
        geo_data = json.loads(geo_response.data.decode('utf-8'))
        
        print(f"Geo response: {geo_data}")
        
        
        # VERIFICAR que hay datos
        if not geo_data or len(geo_data) == 0:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error: Ciudad {CITY} no encontrada')
            }
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        print(f"Coordenadas: {lat}, {lon}")

        # 2. WEATHER
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&APPID={API_KEY}&units=metric"
        print(f"Calling weather URL: {weather_url}")
        
        weather_response = http.request('GET', weather_url)
        weather_data = json.loads(weather_response.data.decode('utf-8'))
        
        print(f"Weather response: {weather_data}")
        
        # VERIFICAR que la respuesta es válida
        if 'main' not in weather_data:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Error: Respuesta inválida de API - {weather_data}')
            }

        # 3. GUARDAR
        item = {
            'city': CITY,
            'timestamp': str(int(time.time())),
            'temp': Decimal(str(weather_data['main']['temp'])),
            'humidity': Decimal(str(weather_data['main']['humidity'])),
            'description': weather_data['weather'][0]['description'],
            'date': get_peru_time().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"Guardando item: {item}")
        table.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Datos guardados correctamente',
                'city': CITY,
                'temp': weather_data['main']['temp'],
                'humidity': weather_data['main']['humidity'],
                'description': weather_data['weather'][0]['description']
            })
        }

    except Exception as e:
        print(f"Error detallado: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
