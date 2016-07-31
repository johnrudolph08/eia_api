import requests
import json
import datetime
import pyowm


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
        self.wether_data = self.get_weather_data()
        self.temps_dict = self.get_temperature(self.wether_data)
        self.temps = self.temps_dict['temp']
        self.max_temps = self.temps_dict['temp_max']
        self.min_temps = self.temps_dict['temp_min']
        self.time = self.get_time(self.wether_data)

    def get_weather_data(self):
        """
        Gets weather forecast from openweathermap
        """
        owm = pyowm.OWM(self.api_key)
        fc = owm.three_hours_forecast('Seattle,US')
        f = fc.get_forecast()
        return f.get_weathers()

    def get_temperature(self, forecast):
        """
        Parses temperature and time from weather objects imbedded in forecast object
        :forecast object returned from get_weather_data
        """
        temps_dict = {'temp': None, 'temp_max': None, 'temp_min': None}
        for key in temps_dict:
            temps_dict[key] = [i.get_temperature(
                'fahrenheit').get(key) for i in forecast]
        return temps_dict

    def get_time(self, forecast):
        """
        Parses temperature and time from weather objects imbedded in forecast object
        :forecast object returned from get_weather_data
        """
        time_3hr = [datetime.datetime.fromtimestamp(i.get_reference_time()).strftime('%Y-%m-%d %H:%M:%S')
                    for i in forecast]
        time1 = datetime.datetime.strptime(time_3hr[0], '%Y-%m-%d %H:%M:%S')
        time2 = datetime.datetime.strptime(time_3hr[-1], '%Y-%m-%d %H:%M:%S')
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
