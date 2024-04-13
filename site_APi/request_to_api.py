from datetime import date
import json

import requests
from pydantic import Json

from config_data.config import SiteSettings

data = SiteSettings()


def get_tickets_price(orig: str = None, dest: str = None, dep_date: date = date.today(),
                      ret_date: date = None, way: str = "false") -> Json:
    url = f"https://api.travelpayouts.com/aviasales/v3/prices_for_dates?"

    querystring = {"origin": orig, "destination": dest,
                   "departure_at": dep_date, "return_at": ret_date, "one_way": way}

    headers = {
        "X-Access-Token": data.avia_token.get_secret_value(),
        "X-RapidAPI-Key": data.api_key.get_secret_value()
    }

    response = requests.get(url, headers=headers, params=querystring)
    response_json = json.loads(response.text)

    return response_json


def get_iata_code(origin: str = None, destination: str = None):
    response = requests.get(f"https://www.travelpayouts.com/widgets_suggest_params?q=%20{origin}%20{destination}")
    response_json = json.loads(response.text)
    return response_json


def get_weather(city: str = None) -> Json:
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"q={city}&appid={data.weather_key.get_secret_value()}&units=metric&lang=ru"
    )
    response_json = json.loads(response.text)
    return response_json


# def get_icon(icon: str = None):
#     response = requests.get(f"https://openweathermap.org/img/wn/{icon}@2x.png")
#     # response_json = json.loads(response.text)
#     return response
#
# print(get_icon('01d'))

if __name__ == '__main__':
    get_tickets_price()
    get_iata_code()
    get_weather()
