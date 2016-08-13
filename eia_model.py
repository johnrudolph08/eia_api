import requests
import json
import pyowm
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from datetime import datetime

# TODO NEED TO CREATE REGRESSION
# LIMIT HISTORICAL OBS TO 24*7*5 obs (5 weeks of data)
# POSSIBLE INCLUSION OF AR(1) TERM


class GetEnergy(object):
    """
    A class to capture an EIA API call
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
        """
        Creates a pandas dataframe of data key in json returned from get_series
        :param json: is an eia json object
        """
        df_dict = {}
        for series in json['series']:
            df = pd.DataFrame(self.get_values(series), index=self.get_dates(series),
                              columns=['values'])
            df_dict[series['series_id']] = df
        return df_dict

    def get_dates(self, series):
        """Parse dates from eia json['series']
        :param series: a series object returned by eia json['series']
        """
        # create a dict to look up datetime frequency values
        freq = {'A': '%Y', 'M': '%Y%m', 'W': '%Y%m%d',
                'D': '%Y%m%d', 'H': '%Y%m%d %H'}
        date_list = []
        for x in series['data']:
            # need to add this ugly bit to remove hourly time format from EIA
            time = x[0].replace('T', ' ')
            time = time.replace('Z', '')
            date_list.append(datetime.strptime(
                time, freq[series['f']]).strftime('%Y-%m-%d %H:%M:%S'))
        return date_list

    def get_values(self, series):
        """Parse values from eia json['series']
        :param series: a series object returned by eia json['series']
        """
        return [value[1] for value in series['data']]


class GetWeatherForecast(object):
    """
    A class to capture an pyowm weather forecast call
    """

    owm_url = 'http://api.openweathermap.org/data/2.5/forecast/city?id={}&APPID={}&units={}'

    def __init__(self, api_key, city_id, units=None):
        """
        Create pyowm forecast object and return related attributes
        :param api_key: a valid Open Weath Map Api-Key
        :param city_id: a valid Open Weather Map city ID
        :param units: default is Kelvin, imperial=Fahrenheight
        """
        self.api_key = api_key
        self.city_id = city_id
        self.units = units
        self.json = self.get_series()
        self.weather_detail = self.create_dataframes(self.json)
        self.hourly_time = self.get_time_hourly(self.weather_detail)
        self.hourly_temps = self.interpolate_weather(self.weather_detail,
                                                     self.hourly_time, 'temp')

    def get_series(self):
        """
        Calls the EIA API with supplied api_key on init and series_id and return json
        """
        owm_req = requests.get(self.owm_url.format(
            self.city_id, self.api_key, self.units))
        return json.loads(owm_req.text)

    def create_dataframes(self, json):
        """
        Creates a pandas dataframe of data key in json returned from get_series
        :param json: is an owm forecast json object
        """
        time_dict = {}
        # first loop through each 3 hr interval in forecast
        for i in json['list']:
            time = datetime.strptime(i['dt_txt'], '%Y-%m-%d %H:%M:%S')
            temps_dict = {'temp': None, 'temp_max': None, 'temp_min': None}
            # create nested dict for each temp attribute
            for j in temps_dict:
                temps_dict[j] = i['main'][j]
            time_dict[time] = temps_dict
        return pd.DataFrame.from_dict(time_dict, orient='index')

    def interpolate_weather(self, weather_detail, time, key):
        """
        Interpolates the 3hr forecast to an hourly forecast using cubic interpolation
        :param weather_detail is dataframe weather attributes returned from get_weather_detail
        :param key is weather detail dataframe column (temp, temp_max or temp_min)
        """
        date_len = len(weather_detail.index)
        date_axis = np.linspace(1, date_len, date_len, endpoint=True)
        f_cubic = interp1d(date_axis, weather_detail[key])
        temp_int = f_cubic(np.linspace(
            1, date_len, num=date_len * 3 - 2, endpoint=True))
        return pd.DataFrame(temp_int.tolist(), index=time)

    def get_time_hourly(self, weather_detail):
        """
        Parses temperature and time from weather objects imbedded in forecast object
        :param weather detail is dictionary returned from get_weather_detail
        """
        min_time, max_time = weather_detail.index.min(), weather_detail.index.max()
        return pd.date_range(min_time, max_time, freq='H')
