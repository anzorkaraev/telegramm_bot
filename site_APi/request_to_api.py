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

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
        response_json = json.loads(response.text)

        return response_json
    except requests.exceptions.Timeout:
        return 'error'


def get_iata_code(origin: str = None, destination: str = None):
    try:
        response = requests.get(
            f"https://www.travelpayouts.com/widgets_suggest_params?q=%20{origin}%20{destination}",
            timeout=5
        )
        response_json = json.loads(response.text)
        return response_json
    except requests.exceptions.Timeout:
        return 'error'


def get_weather(city: str = None) -> Json:
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={data.weather_key.get_secret_value()}&units=metric&lang=ru", timeout=5
        )
        response_json = json.loads(response.text)
        return response_json
    except requests.exceptions.Timeout:
        return 'error'


if __name__ == '__main__':
    get_tickets_price()
    get_iata_code()
    get_weather()
