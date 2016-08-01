import requests
import json
import datetime
import pyowm
import numpy as np
from scipy.interpolate import interp1d


class CallApi:
    """
    Class the returns an eia_api object
    """

    eia_url = 'http://api.eia.gov/series/'

    def __init__(self, api_key, *args):
        """
        Create eia_api object and related attriobutes from json
        :param api_key: an API key that is provided by EIA
        :param *args: The series id (also called source key) is a
                       case-insensitive string consisting of letters, numbers, dashes
                       ("-") and periods (".") that uniquely identifies an EIA series\
                       multiple series can be submitted by comma separation ex: api_key, s1, s2
        """
        self.api_key = api_key
        self.series_id = [";".join(args)]
        self.json = self.get_series()
        self.create_atttributes()

    def get_series(self):
        """
        Calls the EIA API with supplied api_key on init and series_id and return json
        """
        api_parms = (
            ('api_key', self.api_key),
            ('series_id', self.series_id),
        )
        eia_req = requests.get(self.eia_url, params=api_parms)
        return json.loads(eia_req.text)

    def create_atttributes(self):
        """
        Set class attributes for each dict item from returned json
        """
        for key, value in self.json.items():
            # to handle request key of JSON that returns a nested dictionary
            if isinstance(value, dict):
                setattr(self, key, value)
            # to handle series key of JSON that returns a list with nested
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    setattr(self, 'series_{}'.format(i + 1), item)


class GetWeather:

    def __init__(self, api_key):
        self.api_key = api_key
        self.wether = self.get_weather_data('Seattle,US')
        self.weather_detail = self.get_weather_detail(self.wether)
        self.time_1hr = self.get_time_1hr(self.weather_detail)
        self.temps = self.interpolate_weather(self.weather_detail, 'temp')

    def get_weather_data(self, location):
        """
        Gets weather forecast from openweathermap
        """
        owm = pyowm.OWM(self.api_key)
        fc = owm.three_hours_forecast(location)
        f = fc.get_forecast()
        return f.get_weathers()

    def get_weather_detail(self, weather):
        """
        Returns a nested dictionary where first key is date and second key is temp attrs
        :param weather is a object from get_weather_data
        """
        time_dict = {}
        # first loop through each 3 hr interval in forecast
        for i in weather:
            time = datetime.datetime.fromtimestamp(
                i.get_reference_time()).strftime('%Y-%m-%d %H:%M:%S')
            temps_dict = {'temp': None, 'temp_max': None, 'temp_min': None}
            # create nested dict for each temp attribute
            for j in temps_dict:
                temps_dict[j] = i.get_temperature('fahrenheit').get(j)
            time_dict[time] = temps_dict

        return time_dict

    def interpolate_weather(self, weather_detail, key):
        temps = np.asarray([weather_detail[i][key] for i in weather_detail])
        x = np.linspace(1, len(temps), num=len(temps), endpoint=True)
        f_cubic = interp1d(x, temps, kind='cubic')
        temp_int = f_cubic(np.linspace(1, len(temps), num=len(temps) * 3, endpoint=True))
        return temp_int.tolist()

    def get_time_1hr(self, weather_detail):
        """
        Parses temperature and time from weather objects imbedded in forecast object
        :param weather detail is dictionary returned from get_weather_detail
        """
        time1 = datetime.datetime.strptime(
            min(weather_detail), '%Y-%m-%d %H:%M:%S')
        time2 = datetime.datetime.strptime(
            max(weather_detail), '%Y-%m-%d %H:%M:%S')
        dif = int((time2 - time1).total_seconds() / 3600)
        time_1hr = [(time1 + datetime.timedelta(hours=x)).strftime('%Y-%m-%d %H:%M:%S')
                    for x in range(dif + 1)]
        return time_1hr


def create_datetime(series):
    """
    Creates a list of datetimes from eia_json
    :param series is an eia series list of attributes
    """
    freq = {'A': '%Y', 'M': '%Y%m', 'W': '%Y%m%d', 'D': '%Y%m%d'}
    date_list = [datetime.datetime.strptime(x[0], freq[series['f']]).strftime(
        '%Y-%m-%d %H:%M:%S') for x in series['data']]
    return date_list


def create_values(series):
    """
    Creates a list of values
    :param series is an eia series list of attributes
    """
    return [x[1] for x in series['data']]
