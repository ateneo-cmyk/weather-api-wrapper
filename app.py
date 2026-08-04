from flask import Flask, render_template
import os 
import requests
from dotenv import load_dotenv 
import json
import redis

load_dotenv()

app = Flask(__name__)

redis_client = redis.Redis(host='localhost', port =6379, db = 0, decode_responses=True)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather/<city>')
def get_weather(city):
    cache_key = f"clima:{city.lower()}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        print("Obteniendo datos del clima desde Redis...")
        return json.loads(cached_data)    
    print("Obtenido desde OpenWeatherMap!")
    api_key = os.getenv('API_KEY')
    url_externa = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=es"
    respuesta_externa = requests.get(url_externa)
    
    if respuesta_externa.status_code != 200:
        return {"error": f"No se pudo obtener la información del clima de {city}"}
    
    datos_clima = respuesta_externa.json()
    
   

    clima_limpio = {
        "ciudad": datos_clima["name"],
        "temperatura": datos_clima["main"]["temp"],
        "sensacion_termica": datos_clima["main"]["feels_like"],
        "descripcion": datos_clima["weather"][0]["description"]
    }
    
    redis_client.setex(cache_key, 3600, json.dumps(clima_limpio))
    
    return clima_limpio 

if __name__ == '__main__':
    app.run(debug=True)
    
    