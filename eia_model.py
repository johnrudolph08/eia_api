import requests
import json
import pyowm
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from datetime import datetime


class GetEnergy(object):
    """
    Class the beturns an eia_api object
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
        self.df = self.create_dataframes(self.json)

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

    def create_dataframes(self, json):
        df_dict = {}
        for series in json['series']:
            df = pd.DataFrame(self.get_values(series), index=self.get_dates(series),
                              columns=['values'])
            df_dict[series['series_id']] = df
        return df_dict

    @staticmethod
    def get_dates(series):
        """Parse dates from eia json['series']
        :param series: a series object returned by eia json['series']
        """
        freq = {'A': '%Y', 'M': '%Y%m', 'W': '%Y%m%d', 'D': '%Y%m%d'}
        date_list = [datetime.strptime(x[0], freq[series['f']]).strftime(
            '%Y-%m-%d %H:%M:%S') for x in series['data']]
        return date_list

    @staticmethod
    def get_values(series):
        """Parse values from eia json['series']
        :param series: a series object returned by eia json['series']
        """
        return [value[1] for value in series['data']]


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
        """
        Interpolates the 3hr forecast to an hourly forecast using cubic interpolation
        :param weather_detail is dict object of weather attributes returned from get_weather_detail
        :param key is dict key to return temperature (temp, temp_max or temp_min)
        """
        # TODO need to sort weather detail by date !!!arrgrggg
        temps = np.asarray([weather_detail[i][key] for i in weather_detail])
        x = np.linspace(1, len(temps), num=len(temps), endpoint=True)
        # create cubic interpolation object based on 3 hr temp forecast
        f_cubic = interp1d(x, temps)
        # apply cubic interpolation to hourly observations
        temp_int = f_cubic(np.linspace(
            1, len(temps), num=len(temps) * 3, endpoint=True))
        return temp_int.tolist()

    def get_time_1hr(self, weather_detail):
        """
        Parses temperature and time from weather objects imbedded in forecast object
        :param weather detail is dictionary returned from get_weather_detail
        """
        time1 = datetime.strptime(
            min(weather_detail), '%Y-%m-%d %H:%M:%S')
        time2 = datetime.strptime(
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
    date_list = [datetime.strptime(x[0], freq[series['f']]).strftime(
        '%Y-%m-%d %H:%M:%S') for x in series['data']]
    return date_list


def create_values(series):
    """
    Creates a list of values
    :param series is an eia series list of attributes
    """
    return [x[1] for x in series['data']]
