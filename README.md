## Телеграмм Бот  
### Описание
Бот для поиска авиабилетов. Также бот имеет возможность узнать прогноз погоды в точке прибытия

Для поиска билетов будет использован следующий API:
https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com/v1/prices/calendar
##### Пример запроса

```python
import requests

url = "https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com/v1/prices/calendar"
querystring = {"calendar_type":"departure_date","destination":"BCN","origin":"MOW","depart_date":"2024-03-04","currency":"RUB","return_date":"2024-03-14"}

headers = {
    "X-Access-Token": "*************",
    "X-RapidAPI-Key": "*************",
    "X-RapidAPI-Host": "https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
```

##### Пример ответа

```python
data: {
        "2024-03-03": {
            "origin": "MOW",
            "destination": "BCN",
            "airline": "EK",
            "departure_at": "2024-03-03T23:30:00+03:00",
            "return_at": "2024-03-13T20:25:00+01:00",
            "expires_at": "2024-03-03T21:19:50Z",
            "price": 173175,
            "flight_number": 132,
            "transfers": 1
        }}
```

API из примера использует IATA коды городов. Для их получения использую следующий API: https://www.travelpayouts.com/widgets_suggest_params?q=search,  
где вместо search подставляется требуемая фраза.

##### Пример запроса

```python
import requests

response = requests.get("https://www.travelpayouts.com/widgets_suggest_params?q=Из%20Москвы%20в%20Лондон")
```

##### Пример ответа

```python
var = {
    'destination': {
        'iata': 'BLA',
        'name': 'Barcelona'
    },
    'origin': {
        'iata': 'MOW',
        'name': 'Moscow'
    }}
```

Пользователь, при желании, сможет узнать какая погода в точке прибытия. Для этго использую следующий API:  
https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}

##### Пример запроса
```python
import requests

response = requests.get("https://api.openweathermap.org/data/2.5/weather?q=Moscow&appid={API_key}")
```

##### Пример ответа

```python
var = {'base': 'stations',
       'clouds': {'all': 77},
       'cod': 200,
       'coord': {'lat': 55.7522, 'lon': 37.6156},
       'dt': 1709497692,
       'id': 524901,
       'main': {'feels_like': -5.37,
                'grnd_level': 1013,
                'humidity': 100,
                'pressure': 1032,
                'sea_level': 1032,
                'temp': -2.65,
                'temp_max': -1.76,
                'temp_min': -5.9},
       'name': 'Moscow',
       'sys': {'country': 'RU',
               'id': 9027,
               'sunrise': 1709439317,
               'sunset': 1709478474,
               'type': 1},
       'timezone': 10800,
       'visibility': 4744,
       'weather': [{'description': 'broken clouds',
                    'icon': '04n',
                    'id': 803,
                    'main': 'Clouds'}],
       'wind': {'deg': 126, 'gust': 3.14, 'speed': 1.88}}
```